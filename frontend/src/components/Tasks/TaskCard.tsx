import {
  Card,
  CardContent,
  Typography,
  Box,
  Stack,
  Chip,
  IconButton,
  Tooltip,
  Divider,
} from "@mui/material";
import { Delete, DoneAll, Edit } from "@mui/icons-material";
import type { Task } from "../../services/tasksService";
import Utils from "../../services/utils";
import { StatusChip, PriorityChip } from "./TaskChips";

interface TaskCardProps {
  task: Task;
  onComplete: (task: Task) => void;
  onDelete: (task: Task) => void;
  onEdit: (task: Task) => void;
  onRequestComplete?: (task: Task) => void;
}

export default function TaskCard({
  task,
  onComplete,
  onDelete,
  onEdit,
  onRequestComplete,
}: TaskCardProps) {
  const due = task.due_date
    ? (() => {
        try {
          return new Date(task.due_date).toLocaleDateString();
        } catch {
          try {
            return Utils.convertToDate(
              String(task.due_date)
            ).toLocaleDateString();
          } catch {
            return "";
          }
        }
      })()
    : "";

  return (
    <Card
      sx={{
        border: "1px solid rgba(233, 30, 99, 0.12)",
        borderRadius: 2,
        boxShadow: "0 2px 6px rgba(0,0,0,0.06)",
      }}
    >
      <CardContent sx={{ p: 2.25, direction: "rtl" }}>
        {/* Header: Title + Status */}
        <Box
          sx={{
            display: "flex",
            alignItems: "flex-start",
            justifyContent: "space-between",
            mb: 1,
            gap: 1,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              textAlign: "right",
              fontSize: "1.05rem",
              fontWeight: 600,
              lineHeight: 1.25,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
              wordBreak: "break-word",
              pr: 1,
            }}
            title={task.title}
          >
            {task.title}
          </Typography>

          <StatusChip status={task.status} />
        </Box>

        {/* Description */}
        {task.description && (
          <Typography
            variant="body2"
            color="text.secondary"
            sx={{
              textAlign: "right",
              mb: 1.25,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
              lineHeight: 1.35,
              wordBreak: "break-word",
            }}
            title={task.description}
          >
            {task.description}
          </Typography>
        )}

        {/* Meta chips: type + priority */}
        <Stack
          direction="row"
          spacing={0.75}
          flexWrap="wrap"
          useFlexGap
          sx={{ mb: 1.25 }}
        >
          <Chip size="small" variant="outlined" label={task.task_type} />
          <PriorityChip priority={task.priority} />
          {task.reason && (
            <Chip size="small" variant="outlined" label={task.reason} />
          )}
        </Stack>

        <Divider sx={{ my: 1 }} />

        {/* Footer: week/due on left, actions on right */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 1,
          }}
        >
          <Stack direction="row" spacing={0.75} flexWrap="wrap" useFlexGap>
            {(typeof task.start_week === "number" ||
              typeof task.pregnancy_week === "number") && (
              <Chip
                size="small"
                variant="outlined"
                label={`Week ${(task.start_week ?? task.pregnancy_week)!}${
                  typeof task.end_week === "number" ? `–${task.end_week}` : ""
                }`}
              />
            )}
            {due && (
              <Chip size="small" variant="outlined" label={`Due ${due}`} />
            )}
          </Stack>

          <Stack direction="row" spacing={0.5} sx={{ flexShrink: 0 }}>
            <Tooltip title="Edit">
              <IconButton
                size="small"
                onClick={() => onEdit(task)}
                aria-label="edit-task"
              >
                <Edit sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
            <Tooltip title="Mark as completed">
              <span>
                <IconButton
                  size="small"
                  onClick={() =>
                    onRequestComplete
                      ? onRequestComplete(task)
                      : onComplete(task)
                  }
                  disabled={task.status === "completed"}
                  color={task.status === "completed" ? "default" : "success"}
                  aria-label="complete-task"
                >
                  <DoneAll sx={{ fontSize: 18 }} />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Delete">
              <IconButton
                size="small"
                color="error"
                onClick={() => onDelete(task)}
                aria-label="delete-task"
              >
                <Delete sx={{ fontSize: 18 }} />
              </IconButton>
            </Tooltip>
          </Stack>
        </Box>
      </CardContent>
    </Card>
  );
}
