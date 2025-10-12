import { Chip } from "@mui/material";
import { useMemo } from "react";
import type { Task } from "../../services/tasksService";

export function StatusChip({ status }: { status: Task["status"] }) {
  const color = useMemo(() => {
    switch (status) {
      case "completed":
        return "success";
      case "cancelled":
        return "default";
      case "postponed":
        return "warning";
      default:
        return "info";
    }
  }, [status]);

  return <Chip size="small" color={color as any} label={status} />;
}

export function PriorityChip({ priority }: { priority: Task["priority"] }) {
  const color = useMemo(() => {
    switch (priority) {
      case "Urgent":
        return "error";
      case "High":
        return "warning";
      case "Medium":
        return "info";
      default:
        return "default";
    }
  }, [priority]);

  return <Chip size="small" color={color as any} label={priority} />;
}
