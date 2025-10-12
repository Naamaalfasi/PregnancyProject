import { Box, Card, CardContent, Typography, Stack, Chip } from "@mui/material";
import TaskCard from "./TaskCard";
import TaskFilters, { type FilterOptions } from "./TaskFilters";
import type { Task } from "../../services/tasksService";
import { PriorityChip } from "./TaskChips";
import { useState } from "react";

interface TaskListProps {
  tasks: Task[];
  loading: boolean;
  onComplete: (task: Task) => void;
  onDelete: (task: Task) => void;
  onEdit: (task: Task) => void;
  onRequestComplete?: (task: Task) => void;
  onCreate: () => void;
  currentPregnancyWeek?: number;
}

export default function TaskList({
  tasks,
  loading,
  onComplete,
  onDelete,
  onEdit,
  onRequestComplete,
  onCreate,
  currentPregnancyWeek,
}: TaskListProps) {
  const [filters, setFilters] = useState<FilterOptions>({
    timeRange: "upcoming",
  });

  if (loading) return <Typography>Loading tasks…</Typography>;

  // פונקציית סינון
  const filterTasks = (tasks: Task[], filters: FilterOptions): Task[] => {
    return tasks.filter((task) => {
      // סינון לפי טווח זמן
      if (filters.timeRange === "upcoming" && currentPregnancyWeek) {
        const startWeek = task.start_week ?? task.pregnancy_week;
        const endWeek = task.end_week ?? task.pregnancy_week ?? startWeek;

        if (!startWeek) return false;

        // בדיקה אם השבוע הנוכחי חופף לטווח הביצוע של המטלה
        // או שהמטלה צריכה להתבצע בטווח של 5 שבועות מהשבוע הנוכחי
        const isInTaskRange =
          currentPregnancyWeek >= startWeek && currentPregnancyWeek <= endWeek;
        const isInUpcomingRange =
          startWeek >= currentPregnancyWeek &&
          startWeek <= currentPregnancyWeek + 5;

        if (!isInTaskRange && !isInUpcomingRange) {
          return false;
        }
      } else if (filters.timeRange === "pending") {
        if (task.status === "completed") return false;
      }

      // סינון לפי עדיפות
      if (filters.priority && task.priority !== filters.priority) {
        return false;
      }

      // סינון לפי סוג מטלה
      if (filters.taskType && task.task_type !== filters.taskType) {
        return false;
      }

      return true;
    });
  };

  const filteredTasks = filterTasks(tasks, filters);
  const completedTasks = tasks.filter((task) => task.status === "completed");
  const pendingTasks = filteredTasks.filter(
    (task) => task.status !== "completed"
  );

  // מיון המטלות לפי start_week
  const sortedPendingTasks = [...pendingTasks].sort((a, b) => {
    const aWeek = a.start_week ?? a.pregnancy_week ?? 0;
    const bWeek = b.start_week ?? b.pregnancy_week ?? 0;
    return aWeek - bWeek;
  });

  if (!tasks.length) {
    return (
      <Card>
        <CardContent>
          <Typography>No tasks yet.</Typography>
          <Typography variant="body2" color="text.secondary">
            Click "Generate Standard Tasks" to populate recommended tasks based
            on your stage.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box sx={{ direction: "rtl" }}>
      {/* פילטרים */}
      <TaskFilters
        currentPregnancyWeek={currentPregnancyWeek}
        onFiltersChange={setFilters}
        tasks={tasks}
        filteredTasks={filteredTasks}
      />

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            md: "2fr 1fr",
          },
          gap: 3,
        }}
      >
        {/* צד שמאל - מטלות מסוננות */}
        <Box>
          <Stack spacing={2}>
            {/* Create Task tile */}
            <Box
              onClick={onCreate}
              sx={{
                height: 60,
                border: "2px dashed rgba(233, 30, 99, 0.35)",
                borderRadius: 2,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "rgba(233,30,99,0.8)",
                cursor: "pointer",
                transition: "all .2s ease",
                background: "rgba(233,30,99,0.02)",
                "&:hover": {
                  background: "rgba(233,30,99,0.06)",
                  borderColor: "rgba(233,30,99,0.6)",
                },
                fontWeight: 600,
                fontSize: "0.9rem",
              }}
              aria-label="Create Task"
            >
              + Create Task
            </Box>

            {sortedPendingTasks.length > 0 ? (
              sortedPendingTasks.map((task) => (
                <TaskCard
                  key={task.task_id}
                  task={task}
                  onComplete={onComplete}
                  onDelete={onDelete}
                  onEdit={onEdit}
                  onRequestComplete={onRequestComplete}
                />
              ))
            ) : (
              <Card>
                <CardContent>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ textAlign: "right" }}
                  >
                    לא נמצאו מטלות לפי הסינון שנבחר
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Stack>
        </Box>

        {/* צד ימין - מטלות שבוצעו */}
        <Box>
          <Card sx={{ position: "sticky", top: 20 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, textAlign: "right" }}>
                מטלות שבוצעו
              </Typography>

              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2, textAlign: "right" }}
              >
                {completedTasks.length} מטלות הושלמו
              </Typography>

              {completedTasks.length > 0 ? (
                <Stack spacing={1}>
                  {completedTasks.slice(0, 8).map((task) => (
                    <Box
                      key={task.task_id}
                      sx={{
                        p: 1.5,
                        border: "1px solid rgba(76, 175, 80, 0.3)",
                        borderRadius: 1,
                        backgroundColor: "rgba(76, 175, 80, 0.05)",
                      }}
                    >
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, textAlign: "right", mb: 0.5 }}
                      >
                        {task.title}
                      </Typography>
                      {task.completed_at && (
                        <Typography
                          variant="caption"
                          color="text.secondary"
                          sx={{ textAlign: "right", display: "block" }}
                        >
                          הושלם:{" "}
                          {new Date(task.completed_at).toLocaleDateString()}
                        </Typography>
                      )}
                      <Stack
                        direction="row"
                        spacing={0.5}
                        sx={{ mt: 1, justifyContent: "flex-end" }}
                      >
                        <Chip
                          size="small"
                          variant="outlined"
                          label={task.task_type}
                        />
                        <PriorityChip priority={task.priority} />
                      </Stack>
                    </Box>
                  ))}
                  {completedTasks.length > 8 && (
                    <Typography
                      variant="caption"
                      color="text.secondary"
                      sx={{ textAlign: "right", mt: 1 }}
                    >
                      ועוד {completedTasks.length - 8} מטלות...
                    </Typography>
                  )}
                </Stack>
              ) : (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ textAlign: "right" }}
                >
                  עדיין לא בוצעו מטלות
                </Typography>
              )}
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>
  );
}
