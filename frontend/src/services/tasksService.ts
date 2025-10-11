export type TaskType =
  | "Medical_checkup"
  | "Test"
  | "Preparation"
  | "Shopping"
  | "Documentation"
  | "Emergency";
export type TaskPriority = "Low" | "Medium" | "High" | "Urgent";
export type TaskStatus = "pending" | "completed" | "cancelled" | "postponed";
export type TaskSource = "agent" | "user";
export type TaskReason =
  | "standard_schedule"
  | "doctor_recommendation"
  | "test_analysis"
  | "other";

export interface Task {
  task_id: string;
  user_id: string;
  title: string;
  description?: string;
  task_type: TaskType;
  priority: TaskPriority;
  status: TaskStatus;
  completed_at?: string | null;
  start_week?: number | null;
  end_week?: number | null;
  created_at: string;
  source: TaskSource;
  reason: TaskReason;
  related_links?: string[] | null;
  updated_at?: string | null;
  [key: string]: any;
}

export interface TaskCreate {
  title: string;
  description?: string;
  task_type: TaskType;
  priority?: TaskPriority;
  start_week?: number | null;
  end_week?: number | null;
  source?: TaskSource;
  reason?: TaskReason;
  related_links?: string[] | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  task_type?: TaskType;
  priority?: TaskPriority;
  start_week?: number | null;
  end_week?: number | null;
  source?: TaskSource;
  reason?: TaskReason;
  related_links?: string[] | null;
  notes?: string;
  status?: TaskStatus;
  completed_at?: string | null;
}

class TasksService {
  private baseURL = "http://localhost:8000";

  async getUserTasks(
    userId: string
  ): Promise<{ success: boolean; tasks?: Task[]; error?: string }> {
    try {
      const response = await fetch(`${this.baseURL}/users/${userId}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        return {
          success: false,
          error: "Failed to fetch user profile",
        };
      }

      const user = await response.json();
      let tasks = Array.isArray(user?.tasks) ? user.tasks : [];
      tasks = tasks.map((t: Task) => {
        if (
          (t.start_week === null || t.start_week === undefined) &&
          typeof t.pregnancy_week === "number"
        ) {
          return {
            ...t,
            start_week: t.pregnancy_week,
            end_week: t.pregnancy_week,
          };
        }
        return t;
      });

      return { success: true, tasks };
    } catch (error) {
      console.error("Get user tasks error:", error);
      return {
        success: false,
        error: "Network error. Please check your connection.",
      };
    }
  }

  async createStandardTasks(userId: string): Promise<{
    success: boolean;
    message?: string;
    tasks?: Task[];
    error?: string;
  }> {
    try {
      const response = await fetch(`${this.baseURL}/tasks/standard`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userId), // שליחת userId כ-string ב-body
      });

      if (!response.ok) {
        return {
          success: false,
          error: "Failed to create standard tasks",
        };
      }

      const result = await response.json();
      return {
        success: true,
        message: result.message,
        tasks: result.tasks,
      };
    } catch (error) {
      console.error("Create standard tasks error:", error);
      return {
        success: false,
        error: "Network error. Please check your connection.",
      };
    }
  }

  async createTask(
    userId: string,
    data: TaskCreate
  ): Promise<{ success: boolean; task?: Task; error?: string }> {
    try {
      const response = await fetch(`${this.baseURL}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, task_data: data }), // שליחת userId ב-body
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: errorData.detail || "Failed to create task",
        };
      }

      const task = await response.json();
      return { success: true, task };
    } catch (error) {
      console.error("Create task error:", error);
      return {
        success: false,
        error: "Network error. Please check your connection.",
      };
    }
  }

  async updateTask(
    taskId: string,
    data: TaskUpdate
  ): Promise<{ success: boolean; task?: Task; error?: string }> {
    try {
      const response = await fetch(`${this.baseURL}/tasks/${taskId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        // Try to get error message from response
        const errorData = await response.json().catch(() => ({}));
        return {
          success: false,
          error: errorData.detail || "Failed to update task",
        };
      }

      const task = await response.json();
      return { success: true, task };
    } catch (error) {
      console.error("Update task error:", error);
      return {
        success: false,
        error: "Network error. Please check your connection.",
      };
    }
  }

  async deleteTask(
    taskId: string
  ): Promise<{ success: boolean; error?: string }> {
    try {
      const response = await fetch(`${this.baseURL}/tasks/${taskId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        return {
          success: false,
          error: "Failed to delete task",
        };
      }

      return { success: true };
    } catch (error) {
      console.error("Delete task error:", error);
      return {
        success: false,
        error: "Network error. Please check your connection.",
      };
    }
  }
}

export const tasksService = new TasksService();
