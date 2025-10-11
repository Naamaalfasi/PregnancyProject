import {
  Box,
  Button,
  IconButton,
  Stack,
  Tooltip,
  Typography,
} from "@mui/material";
import { Assignment, Refresh } from "@mui/icons-material";

interface TaskToolbarProps {
  creatingStd: boolean;
  loading: boolean;
  onCreateStandard: () => void;
  onRefresh: () => void;
}

export default function TaskToolbar({
  creatingStd,
  loading,
  onCreateStandard,
  onRefresh,
}: TaskToolbarProps) {
  return (
    <Box
      sx={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        mb: 3,
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
        <Assignment sx={{ fontSize: 36, color: "primary.main" }} />
        <Typography variant="h4">Tasks</Typography>
      </Box>
      <Stack direction="row" spacing={1}>
        <Button
          variant="contained"
          onClick={onCreateStandard}
          disabled={creatingStd}
          sx={{
            background: "linear-gradient(45deg, #e91e63, #9c27b0)",
            "&:hover": { opacity: 0.9 },
          }}
        >
          {creatingStd ? "Creating…" : "Generate Standard Tasks"}
        </Button>
        <Tooltip title="Refresh">
          <span>
            <IconButton onClick={onRefresh} disabled={loading}>
              <Refresh />
            </IconButton>
          </span>
        </Tooltip>
      </Stack>
    </Box>
  );
}
