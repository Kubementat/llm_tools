#!/usr/bin/env python3
"""
Task Queue Processor Module

This module provides functionality for processing tasks from the queue.
It integrates with SequentialTaskExecutor to execute LLM workflows.

Classes:
    TaskProcessor: Manages task execution and status updates
"""

import time
from typing import Optional
from .manager import TaskQueueManager
from .status_tracker import StatusTracker
from .error_handler import ErrorHandler
from ..sequential_task_executor import SequentialTaskExecutor
from sokrates.config import Config

class TaskProcessor:
    """
    Processes tasks from the queue using SequentialTaskExecutor.

    This class provides methods for executing queued tasks,
    handling errors, and managing task lifecycle.

    Attributes:
        manager: TaskQueueManager instance for database operations
        status_tracker: StatusTracker instance for tracking progress
        error_handler: ErrorHandler instance for error management

    Methods:
        process_tasks(): Process pending tasks from the queue
        execute_task(): Execute a single task using SequentialTaskExecutor
    """

    def __init__(self, db_path: Optional[str] = None, logger = None):
        """
        Initializes the TaskProcessor with configured components.

        Args:
            db_path (str, optional): Path to the SQLite database file.
                If None, uses the default from TaskQueueManager.
        """
        self.manager = TaskQueueManager(db_path)
        self.status_tracker = StatusTracker(self.manager)
        self.error_handler = ErrorHandler()
        self.logger = logger
        
    def log_message(self, message):
        if self.logger:
            self.logger.info(message)

    def process_tasks(self, limit: Optional[int] = None):
        """
        Process pending tasks from the queue.

        Args:
            limit (int, optional): Maximum number of tasks to process. If None, processes all.
        """
        try:
            # Get pending tasks
            pending_tasks = self.manager.get_pending_tasks(limit)
            self.log_message(f"Number of pending tasks: {len(pending_tasks)}")

            if not pending_tasks:
                self.log_message("No pending tasks to process.")
                return

            for task in pending_tasks:
                self._process_single_task_file(task)
                time.sleep(1)  # Small delay between tasks

        except Exception as e:
            self.log_message(f"Error processing tasks: {e}")
        finally:
            self.manager.close()

    def _process_single_task_file(self, task):
        """
        Process a single task through execution and status updates.

        Args:
            task (dict): Task information from the queue
        """
        task_id = task['task_id']
        file_path = task['file_path']
        
        executor = SequentialTaskExecutor(
                api_endpoint=Config().api_endpoint,
                api_key=Config().api_key,
                model=Config().default_model,
                temperature=Config().default_model_temperature,
                verbose=True
                )

        try:
            # Update status to in_progress
            self.status_tracker.update_status(task_id, "in_progress")

            # Execute task using SequentialTaskExecutor
            result = executor.execute_tasks_from_file(file_path)

            # Update status to completed with result
            self.status_tracker.update_status(
                task_id,
                "completed",
                result=f"Successfully executed: {result['successful_tasks']}/{result['total_tasks']} tasks"
            )

        except Exception as e:
            # Handle errors with retry logic
            current_attempt = 1

            while True:
                error_info = self.error_handler.log_error(task_id, str(e), current_attempt)

                next_action = self.error_handler.handle_failure(
                    self.manager,
                    task_id,
                    str(e),
                    current_attempt
                )

                if next_action == "retry":
                    self.log_message(f"Retrying task {task_id} (attempt {current_attempt})...")
                    time.sleep(self.error_handler.get_retry_delay(current_attempt))

                    try:
                        # Retry the execution
                        result = executor.execute_tasks_from_file(file_path)

                        self.status_tracker.update_status(
                            task_id,
                            "completed",
                            result=f"Successfully executed on retry {current_attempt}: {result['successful_tasks']}/{result['total_tasks']} tasks"
                        )
                        break  # Successful retry, exit the loop

                    except Exception as retry_e:
                        current_attempt += 1
                        e = retry_e  # Update error for next iteration

                elif next_action == "dead_letter":
                    self.log_message(f"Moving task {task_id} to dead letter queue after max retries")
                    break

                else:  # fail
                    self.log_message(f"Task {task_id} failed permanently: {e}")
                    break