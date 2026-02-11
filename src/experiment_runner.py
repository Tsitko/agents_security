"""
Оркестратор экспериментов с checkpoint системой.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

from .battle_engine import BattleEngine, BattleLog, BattleResult


@dataclass
class ExperimentState:
    """Experiment state for checkpointing."""
    pair_id: str
    pair_name: str
    attacker_model: str
    defender_model: str
    total_experiments: int
    completed_experiments: int
    current_learning: str  # Накопленное обучение attacker
    results: list[dict]  # Результаты завершённых битв
    started_at: str
    last_updated: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ExperimentState":
        return cls(**data)


class ExperimentRunner:
    """Runs experiment series with state saving.
    
    Supports Phase 2 testing with separate output directories.
    """

    def __init__(
        self, 
        config_path: str, 
        results_dir: str = "results",
        checkpoints_dir: str = "checkpoints"
    ):
        self.config_path = Path(config_path)
        self.results_dir = Path(results_dir)
        self.checkpoints_dir = Path(checkpoints_dir)

        # Создаём директории
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        (self.results_dir / "conversations").mkdir(exist_ok=True)
        (self.results_dir / "summaries").mkdir(exist_ok=True)

        # Загружаем конфиг
        with open(self.config_path, encoding="utf-8") as f:
            self.config = json.load(f)

    def get_checkpoint_path(self, pair_id: str) -> Path:
        """Путь к файлу checkpoint."""
        return self.checkpoints_dir / f"{pair_id}_checkpoint.json"

    def load_checkpoint(self, pair_id: str) -> Optional[ExperimentState]:
        """Загружает checkpoint если есть."""
        path = self.get_checkpoint_path(pair_id)
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return ExperimentState.from_dict(json.load(f))
        return None

    def save_checkpoint(self, state: ExperimentState):
        """Сохраняет checkpoint."""
        path = self.get_checkpoint_path(state.pair_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)

    def save_battle_log(self, log: BattleLog):
        """Сохраняет полный лог битвы."""
        filename = f"{log.battle_id}.json"
        path = self.results_dir / "conversations" / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(log.to_dict(), f, ensure_ascii=False, indent=2)

    def save_summary(self, pair_id: str, summary: str, experiment_num: int):
        """Сохраняет суммаризацию."""
        filename = f"{pair_id}_exp{experiment_num:02d}_summary.txt"
        path = self.results_dir / "summaries" / filename
        with open(path, "w", encoding="utf-8") as f:
            f.write(summary)

    def list_pairs(self) -> list[dict]:
        """Список всех пар моделей."""
        return self.config["model_pairs"]

    def get_pair_status(self, pair_id: str) -> dict:
        """Статус эксперимента для пары."""
        state = self.load_checkpoint(pair_id)
        total = self.config["experiments_per_pair"]

        if state is None:
            return {
                "status": "not_started",
                "completed": 0,
                "total": total,
                "wins": {"attacker": 0, "defender": 0, "refused": 0, "error": 0},
            }

        wins = {"attacker": 0, "defender": 0, "refused": 0, "error": 0}
        for r in state.results:
            result = r.get("result", "")
            if result == "attacker_win":
                wins["attacker"] += 1
            elif result in ["defender_win", "max_turns", "attacker_quit"]:
                wins["defender"] += 1
            elif result == "attacker_refused":
                wins["refused"] += 1
            else:
                wins["error"] += 1

        status = "completed" if state.completed_experiments >= total else "in_progress"

        return {
            "status": status,
            "completed": state.completed_experiments,
            "total": total,
            "wins": wins,
        }

    def run_experiment_series(
        self,
        pair_id: str,
        dry_run: bool = False,
    ) -> ExperimentState:
        """
        Запускает серию экспериментов для одной пары моделей.
        Продолжает с checkpoint если есть.
        """
        # Находим пару
        pair = None
        for p in self.config["model_pairs"]:
            if p["id"] == pair_id:
                pair = p
                break

        if pair is None:
            raise ValueError(f"Pair {pair_id} not found in config")

        total_experiments = self.config["experiments_per_pair"]

        # Пытаемся загрузить checkpoint
        state = self.load_checkpoint(pair_id)

        if state is None:
            # Новый эксперимент
            state = ExperimentState(
                pair_id=pair_id,
                pair_name=pair["name"],
                attacker_model=pair["attacker"],
                defender_model=pair["defender"],
                total_experiments=total_experiments,
                completed_experiments=0,
                current_learning="",
                results=[],
                started_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
            )
            print(f"\n{'='*60}")
            print(f"Starting NEW experiment series: {pair['name']}")
            print(f"Attacker: {pair['attacker']}")
            print(f"Defender: {pair['defender']}")
            print(f"Total experiments: {total_experiments}")
            print(f"{'='*60}")
        else:
            # Check if already completed
            if state.completed_experiments >= total_experiments:
                print(f"\n{'='*60}")
                print(f"ALREADY COMPLETED: {pair['name']}")
                print(f"Completed: {state.completed_experiments}/{total_experiments}")
                print(f"{'='*60}")
                return state

            print(f"\n{'='*60}")
            print(f"RESUMING experiment series: {pair['name']}")
            print(f"Completed: {state.completed_experiments}/{total_experiments}")
            print(f"{'='*60}")

        if dry_run:
            print("[DRY RUN] Would run experiments but stopping here")
            return state

        # Создаём движок
        engine = BattleEngine(
            base_url=self.config["lm_studio"]["base_url"],
            attacker_model=pair["attacker"],
            defender_model=pair["defender"],
            attacker_params=self.config["battle_settings"]["attacker_params"],
            defender_params=self.config["battle_settings"]["defender_params"],
            max_turns=self.config["battle_settings"]["max_turns"],
            retry_attempts=self.config["lm_studio"]["retry_attempts"],
            retry_delay=self.config["lm_studio"]["retry_delay_seconds"],
        )

        # Запускаем оставшиеся эксперименты
        start_from = state.completed_experiments + 1

        for exp_num in range(start_from, total_experiments + 1):
            print(f"\n{'#'*60}")
            print(f"# Experiment {exp_num}/{total_experiments}")
            print(f"{'#'*60}")

            battle_id = f"{pair_id}_exp{exp_num:02d}"

            # Запускаем битву
            log = engine.run_battle(
                battle_id=battle_id,
                pair_id=pair_id,
                experiment_number=exp_num,
                attacker_learning=state.current_learning,
            )

            # Сохраняем лог битвы
            self.save_battle_log(log)

            # Суммаризируем и обновляем обучение
            summary = engine.summarize_battle(log)
            log.attacker_learning = summary
            self.save_summary(pair_id, summary, exp_num)

            # Обновляем накопленное обучение
            if state.current_learning:
                state.current_learning += f"\n\n--- Experiment {exp_num} ---\n{summary}"
            else:
                state.current_learning = f"--- Experiment {exp_num} ---\n{summary}"

            # Обновляем состояние
            state.results.append({
                "experiment": exp_num,
                "battle_id": battle_id,
                "result": log.result.value if log.result else "unknown",
                "total_turns": log.total_turns,
                "details": log.result_details,
            })
            state.completed_experiments = exp_num
            state.last_updated = datetime.now().isoformat()

            # Сохраняем checkpoint после каждого эксперимента
            self.save_checkpoint(state)

            print(f"\n[Checkpoint saved] {state.completed_experiments}/{total_experiments} completed")
            print(f"Result: {log.result.value if log.result else 'unknown'}")

        print(f"\n{'='*60}")
        print(f"Series COMPLETED: {pair['name']}")
        print(f"{'='*60}")

        return state

    def print_status(self):
        """Печатает статус всех экспериментов."""
        print("\n" + "=" * 80)
        print("EXPERIMENT STATUS")
        print("=" * 80)

        for pair in self.list_pairs():
            status = self.get_pair_status(pair["id"])
            wins = status["wins"]
            marker = {
                "not_started": "[ ]",
                "in_progress": "[~]",
                "completed": "[x]",
            }[status["status"]]

            parallel = "Yes" if pair["can_run_parallel"] else "No"
            print(f"\n{marker} {pair['id']}: {pair['name']}")
            print(f"    Attacker: {pair['attacker']}")
            print(f"    Defender: {pair['defender']}")
            print(f"    Parallel: {parallel} | {status['completed']}/{status['total']} "
                  f"(A:{wins['attacker']} D:{wins['defender']} R:{wins['refused']} E:{wins['error']})")

        print("\n" + "=" * 80)


def main():
    """CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Agent Security Experiment Runner")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument("--results", default="results", help="Results directory")
    parser.add_argument("--checkpoints", default="checkpoints", help="Checkpoints directory")
    parser.add_argument("--phase2", action="store_true", help="Use Phase 2 directories (results_2, checkpoints_2)")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # status command
    subparsers.add_parser("status", help="Show experiment status")

    # list command
    subparsers.add_parser("list", help="List model pairs")

    # run command
    run_parser = subparsers.add_parser("run", help="Run experiment series")
    run_parser.add_argument("pair_id", help="Pair ID to run (e.g., pair_01)")
    run_parser.add_argument("--dry-run", action="store_true", help="Don't actually run")

    args = parser.parse_args()

    # Use Phase 2 directories if specified
    results_dir = args.results
    checkpoints_dir = args.checkpoints
    if args.phase2:
        results_dir = "results_2"
        checkpoints_dir = "checkpoints_2"

    runner = ExperimentRunner(args.config, results_dir, checkpoints_dir)

    if args.command == "status":
        runner.print_status()

    elif args.command == "list":
        print("\nModel Pairs:")
        for p in runner.list_pairs():
            print(f"  {p['id']}: {p['name']}")
            print(f"    A: {p['attacker']}")
            print(f"    D: {p['defender']}")
            print()

    elif args.command == "run":
        runner.run_experiment_series(
            pair_id=args.pair_id,
            dry_run=args.dry_run,
        )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
