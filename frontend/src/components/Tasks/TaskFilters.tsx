import {
  Box,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Typography,
} from "@mui/material";
import { useState } from "react";
import type { Task, TaskType, TaskPriority } from "../../services/tasksService";

export interface FilterOptions {
  timeRange: "upcoming" | "pending" | "all";
  priority?: TaskPriority;
  taskType?: TaskType;
}

interface TaskFiltersProps {
  currentPregnancyWeek?: number;
  onFiltersChange: (filters: FilterOptions) => void;
  tasks: Task[];
}

export default function TaskFilters({
  currentPregnancyWeek,
  onFiltersChange,
  tasks,
}: TaskFiltersProps) {
  const [filters, setFilters] = useState<FilterOptions>({
    timeRange: "upcoming",
  });

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearFilter = (key: keyof FilterOptions) => {
    const newFilters = { ...filters, [key]: undefined };
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  // סטטיסטיקות
  const upcomingCount = tasks.filter((task) => {
    if (!currentPregnancyWeek) return false;
    const startWeek = task.start_week ?? task.pregnancy_week;
    return (
      startWeek &&
      startWeek >= currentPregnancyWeek &&
      startWeek <= currentPregnancyWeek + 5
    );
  }).length;

  const pendingCount = tasks.filter(
    (task) => task.status !== "completed"
  ).length;

  return (
    <Box sx={{ mb: 3, direction: "rtl" }}>
      <Typography variant="h6" sx={{ mb: 2, textAlign: "right" }}>
        סינון מטלות
      </Typography>

      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
        {/* טווח זמן */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>טווח זמן</InputLabel>
          <Select
            value={filters.timeRange}
            label="טווח זמן"
            onChange={(e) => handleFilterChange("timeRange", e.target.value)}
          >
            <MenuItem value="upcoming">בחודש הקרוב ({upcomingCount})</MenuItem>
            <MenuItem value="pending">שטרם בוצעו ({pendingCount})</MenuItem>
            <MenuItem value="all">הכל</MenuItem>
          </Select>
        </FormControl>

        {/* עדיפות */}
        <FormControl size="small" sx={{ minWidth: 120 }}>
          <InputLabel>עדיפות</InputLabel>
          <Select
            value={filters.priority || ""}
            label="עדיפות"
            onChange={(e) =>
              handleFilterChange("priority", e.target.value || undefined)
            }
          >
            <MenuItem value="">כל העדיפויות</MenuItem>
            <MenuItem value="Urgent">Urgent</MenuItem>
            <MenuItem value="High">High</MenuItem>
            <MenuItem value="Medium">Medium</MenuItem>
            <MenuItem value="Low">Low</MenuItem>
          </Select>
        </FormControl>

        {/* סוג מטלה */}
        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>סוג מטלה</InputLabel>
          <Select
            value={filters.taskType || ""}
            label="סוג מטלה"
            onChange={(e) =>
              handleFilterChange("taskType", e.target.value || undefined)
            }
          >
            <MenuItem value="">כל הסוגים</MenuItem>
            <MenuItem value="Test">Test</MenuItem>
            <MenuItem value="Medical_checkup">Medical_checkup</MenuItem>
            <MenuItem value="Preparation">Preparation</MenuItem>
            <MenuItem value="Shopping">Shopping</MenuItem>
            <MenuItem value="Documentation">Documentation</MenuItem>
            <MenuItem value="Emergency">Emergency</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      {/* תצוגת פילטרים פעילים */}
      <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: "wrap" }}>
        {filters.priority && (
          <Chip
            label={`עדיפות: ${filters.priority}`}
            onDelete={() => clearFilter("priority")}
            size="small"
            color="primary"
            variant="outlined"
          />
        )}
        {filters.taskType && (
          <Chip
            label={`סוג: ${filters.taskType}`}
            onDelete={() => clearFilter("taskType")}
            size="small"
            color="secondary"
            variant="outlined"
          />
        )}
      </Stack>
    </Box>
  );
}
