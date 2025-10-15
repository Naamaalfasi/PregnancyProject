import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  MenuItem,
  Stack,
} from "@mui/material";
import { useState, useEffect } from "react";
import type { Task } from "../../services/tasksService";
import type { TaskType } from "../../services/tasksService";

const priorities = ["Low", "Medium", "High", "Urgent"] as const;
const statuses = ["pending", "completed", "cancelled", "postponed"] as const;
const taskTypes: TaskType[] = [
  "Medical_checkup",
  "Test",
  "Preparation",
  "Shopping",
  "Documentation",
  "Emergency",
];

export default function TaskEditDialog({
  open,
  task,
  onClose,
  onSave,
}: {
  open: boolean;
  task: Task | null;
  onClose: () => void;
  onSave: (data: Partial<Task>) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Task["priority"]>("Medium");
  const [status, setStatus] = useState<Task["status"]>("pending");
  const [taskType, setTaskType] = useState<TaskType>("Test");
  const [startWeek, setStartWeek] = useState<number | "">("");
  const [endWeek, setEndWeek] = useState<number | "">("");

  useEffect(() => {
    if (!task) return;
    setTitle(task.title || "");
    setDescription(task.description || "");
    setPriority(task.priority || "Medium");
    setStatus(task.status || "pending");
    setTaskType(task.task_type || "Test");
    setStartWeek(task.start_week || "");
    setEndWeek(task.end_week || "");
    setEndWeek("");
  }, [task]);

  const handleSave = () => {
    onSave({
      title,
      description,
      priority,
      status,
      task_type: taskType,
      start_week: startWeek === "" ? undefined : Number(startWeek),
      end_week: endWeek === "" ? undefined : Number(endWeek),
    });
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>Edit Task</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            label="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            fullWidth
          />
          <TextField
            label="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            fullWidth
            multiline
            minRows={3}
          />
          <TextField
            label="Task Type"
            select
            value={taskType}
            onChange={(e) => setTaskType(e.target.value as TaskType)}
          >
            {taskTypes.map((t) => (
              <MenuItem key={t} value={t}>
                {t}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Start Week"
            type="number"
            inputProps={{ min: 1, max: 42 }}
            value={startWeek}
            onChange={(e) => {
              const v = e.target.value;
              setStartWeek(v === "" ? "" : Number(v));
            }}
          />
          <TextField
            label="End Week"
            type="number"
            inputProps={{ min: 1, max: 42 }}
            value={endWeek}
            onChange={(e) => {
              const v = e.target.value;
              setEndWeek(v === "" ? "" : Number(v));
            }}
          />
          <TextField
            label="Priority"
            select
            value={priority}
            onChange={(e) => setPriority(e.target.value as Task["priority"])}
          >
            {priorities.map((p) => (
              <MenuItem key={p} value={p}>
                {p}
              </MenuItem>
            ))}
          </TextField>
          <TextField
            label="Status"
            select
            value={status}
            onChange={(e) => setStatus(e.target.value as Task["status"])}
          >
            {statuses.map((s) => (
              <MenuItem key={s} value={s}>
                {s}
              </MenuItem>
            ))}
          </TextField>
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleSave}>
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
}
