import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Stack,
} from "@mui/material";
import { useEffect, useState } from "react";

export default function CompleteTaskDialog({
  open,
  onClose,
  onConfirm,
  initialDate,
}: {
  open: boolean;
  onClose: () => void;
  onConfirm: (isoDate: string) => void;
  initialDate?: string; // yyyy-mm-dd
}) {
  const [date, setDate] = useState<string>("");

  useEffect(() => {
    if (open) {
      if (initialDate) setDate(initialDate);
      else {
        const today = new Date();
        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0');
        const year = today.getFullYear();
        setDate(`${year}-${month}-${day}`);
      }
    }
  }, [open, initialDate]);

  const today = new Date().toISOString().split("T")[0];

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="xs">
      <DialogTitle>mark task as completed</DialogTitle>
      <DialogContent>
        <Stack spacing={2} sx={{ mt: 1 }}>
          <TextField
            label="completion date"
            type="date"
            InputLabelProps={{ shrink: true }}
            value={date}
            onChange={(e) => setDate(e.target.value)}
            inputProps={{ max: today }}
          />
        </Stack>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>cancel</Button>
        <Button
          variant="contained"
          onClick={() => onConfirm(new Date(date).toISOString())}
        >
          שמור
        </Button>
      </DialogActions>
    </Dialog>
  );
}
