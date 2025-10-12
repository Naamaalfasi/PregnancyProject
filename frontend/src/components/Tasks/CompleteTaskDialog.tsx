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
        const d = new Date();
        const yyyy = d.getFullYear();
        const mm = String(d.getMonth() + 1).padStart(2, "0");
        const dd = String(d.getDate()).padStart(2, "0");
        setDate(`${dd}-${mm}-${yyyy}`);
      }
    }
  }, [open, initialDate]);

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
