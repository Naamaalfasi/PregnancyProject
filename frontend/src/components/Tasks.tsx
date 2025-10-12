import { Container, Box, Divider } from "@mui/material";
import TaskToolbar from "./Tasks/TaskToolbar";
import TaskList from "./Tasks/TaskList";
import { useTasks } from "../hooks/useTasks";
import TaskEditDialog from "./Tasks/TaskEditDialog";
import CompleteTaskDialog from "./Tasks/CompleteTaskDialog";
import { useState } from "react";
import type { Task } from "../services/tasksService";
import { tasksService } from "../services/tasksService";
import { authService } from "../services/authService";
import { useEffect } from "react";

export default function Tasks() {
  const {
    tasks,
    loading,
    creatingStd,
    load,
    complete,
    remove,
    createStandard,
    update,
  } = useTasks();

  const [editing, setEditing] = useState<Task | null>(null);

  // complete dialog state
  const [completing, setCompleting] = useState<Task | null>(null);
  const [initialDate, setInitialDate] = useState<string | undefined>(undefined);

  // create dialog state
  const [creating, setCreating] = useState<boolean>(false);
  const [currentPregnancyWeek, setCurrentPregnancyWeek] = useState<
    number | undefined
  >(undefined);

  useEffect(() => {
    const loadUserWeek = async () => {
      const userId = authService.getCurrentUserId();
      if (userId) {
        try {
          const response = await fetch(`http://localhost:8000/users/${userId}`);
          if (response.ok) {
            const user = await response.json();
            setCurrentPregnancyWeek(user.pregnancy_week);
          }
        } catch (error) {
          console.error("Failed to load user pregnancy week:", error);
        }
      }
    };
    loadUserWeek();
  }, []);

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)",
      }}
    >
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <TaskToolbar
          creatingStd={creatingStd}
          loading={loading}
          onCreateStandard={createStandard}
          onRefresh={load}
        />

        <Divider sx={{ mb: 3, borderColor: "rgba(233, 30, 99, 0.2)" }} />

        <TaskList
          tasks={tasks}
          loading={loading}
          onComplete={complete}
          onDelete={remove}
          onEdit={(t) => setEditing(t)}
          onRequestComplete={(t) => {
            setCompleting(t);
            if (t.completed_at) {
              const d = new Date(t.completed_at);
              if (!isNaN(d.getTime())) {
                const yyyy = d.getFullYear();
                const mm = String(d.getMonth() + 1).padStart(2, "0");
                const dd = String(d.getDate()).padStart(2, "0");
                setInitialDate(`${yyyy}-${mm}-${dd}`);
              } else {
                setInitialDate(undefined);
              }
            } else {
              setInitialDate(undefined);
            }
          }}
          onCreate={() => setCreating(true)}
          currentPregnancyWeek={currentPregnancyWeek}
        />

        {/* Edit Task */}
        <TaskEditDialog
          open={!!editing}
          task={editing}
          onClose={() => setEditing(null)}
          onSave={async (data) => {
            if (!editing) return;
            await update(editing.task_id, data);
            setEditing(null);
          }}
        />

        {/* Complete Task */}
        <CompleteTaskDialog
          open={!!completing}
          initialDate={initialDate}
          onClose={() => {
            setCompleting(null);
            setInitialDate(undefined);
          }}
          onConfirm={async (isoDate) => {
            if (!completing) return;
            await update(completing.task_id, {
              status: "completed",
              completed_at: isoDate,
            });
            setCompleting(null);
            setInitialDate(undefined);
          }}
        />

        {/* Create Task */}
        <TaskEditDialog
          open={creating}
          task={null}
          onClose={() => setCreating(false)}
          onSave={async (data: any) => {
            const userId = authService.getCurrentUserId();
            if (!userId) return;

            const payload = {
              title: data.title!,
              description: data.description,
              task_type: data.task_type!,
              priority: data.priority ?? "Medium",
              start_week: data.start_week,
              end_week: data.end_week,
              source: data.source ?? "user",
              reason: data.reason ?? "other",
              related_links: data.related_links,
            } as any;

            const res = await tasksService.createTask(userId, payload);
            if (res?.success) {
              setCreating(false);
              await load();
            }
          }}
        />
      </Container>
    </Box>
  );
}
