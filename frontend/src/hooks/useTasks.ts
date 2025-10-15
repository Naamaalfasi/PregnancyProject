import { useCallback, useEffect, useState } from "react";
import { tasksService, type Task } from "../services/tasksService";
import { authService } from "../services/authService";

export function useTasks() {
  const [userId, setUserId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [creatingStd, setCreatingStd] = useState(false);

  useEffect(() => {
    const currentUserId = authService.getCurrentUserId();
    console.log("Current user ID from localStorage:", currentUserId);
    setUserId(currentUserId);
  }, []);

  const load = useCallback(async () => {
    if (!userId) {
      console.log("No userId, skipping load");
      return;
    }
    console.log("Loading tasks for userId:", userId);
    setLoading(true);
    try {
      const result = await tasksService.getUserTasks(userId);
      console.log("Load result:", result);
      if (result.success && result.tasks) {
        setTasks(result.tasks);
        console.log("Set tasks:", result.tasks);
      }
    } catch (error) {
      console.error("Failed to load tasks:", error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    load();
  }, [load]);

  const complete = useCallback(
    async (task: Task) => {
      try {
        const result = await tasksService.updateTask(task.task_id, {
          status: "completed",
          completed_at: new Date().toISOString(),
        });
        if (result.success) {
          await load();
        }
      } catch (error) {
        console.error("Failed to complete task:", error);
      }
    },
    [load]
  );

  const remove = useCallback(
    async (task: Task) => {
      try {
        const result = await tasksService.deleteTask(task.task_id);
        if (result.success) {
          await load();
        }
      } catch (error) {
        console.error("Failed to delete task:", error);
      }
    },
    [load]
  );

  const createStandard = useCallback(async () => {
    if (!userId) {
      console.log("No userId, cannot create standard tasks");
      return;
    }
    console.log("Creating standard tasks for userId:", userId);
    setCreatingStd(true);
    try {
      const result = await tasksService.createStandardTasks(userId);
      console.log("Create standard tasks result:", result);
      if (result.success) {
        await load();
      }
    } catch (error) {
      console.error("Failed to create standard tasks:", error);
    } finally {
      setCreatingStd(false);
    }
  }, [userId, load]);

  const update = useCallback(
    async (taskId: string, data: Partial<Task>) => {
      const result = await tasksService.updateTask(taskId, data);
      if (result.success) await load();
    },
    [load]
  );

  return {
    tasks,
    loading,
    creatingStd,
    load,
    complete,
    remove,
    createStandard,
    update,
  };
}
