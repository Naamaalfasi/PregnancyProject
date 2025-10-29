import { Card, CardContent, Typography, Box, Chip } from "@mui/material";
import type { Task } from "../../services/tasksService";
import { StatusChip, PriorityChip } from "./TaskChips";

interface CompactTaskCardProps {
  task: Task;
}

export default function CompactTaskCard({ task }: CompactTaskCardProps) {
  return (
    <Card
      sx={{
        border: "1px solid rgba(233, 30, 99, 0.12)",
        borderRadius: 1.5,
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
        mb: 1,
        maxWidth: "600px",
        width: "100%",
        mx: "auto",
        transition: "all 0.2s ease-in-out",
        "&:hover": {
          boxShadow: "0 4px 12px rgba(233, 30, 99, 0.15)",
          borderColor: "rgba(233, 30, 99, 0.3)",
          transform: "translateY(-2px)",
        },
      }}
    >
      <CardContent sx={{ p: 1.5 }}>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            mb: 1,
          }}
        >
          <Typography
            variant="h6"
            sx={{
              fontWeight: 600,
              fontSize: "1rem",
              lineHeight: 1.3,
              flex: 1,
              mr: 1,
            }}
          >
            {task.title}
          </Typography>
          <StatusChip status={task.status} />
        </Box>

        {task.description && (
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              fontSize: "1rem",
              lineHeight: 1.4,
              mb: 1,
              display: "-webkit-box",
              WebkitLineClamp: 2,
              WebkitBoxOrient: "vertical",
              overflow: "hidden",
            }}
          >
            {task.description}
          </Typography>
        )}

        <Box sx={{ display: "flex", gap: 1, flexWrap: "wrap" }}>
          <PriorityChip priority={task.priority} />
          {task.start_week && (
            <Chip
              label={`Week ${task.start_week}`}
              size="small"
              variant="outlined"
              sx={{ fontSize: "0.75rem", height: "24px" }}
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
}
