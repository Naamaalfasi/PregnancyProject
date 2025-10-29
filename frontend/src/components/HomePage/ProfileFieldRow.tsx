import { Box, Typography } from "@mui/material";

export default function ProfileFieldRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <Box sx={{ py: 1, px: 0.5, width: "100%" }}>
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 1.25,
          flexWrap: "wrap",
        }}
      >
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 0.75,
            px: 1.25,
            py: 0.4,
            borderRadius: 999,
            bgcolor: "rgba(250,250,252,0.9)",
            border: "1px solid rgba(0,0,0,0.06)",
          }}
        >
          {icon}
          <Typography
            component="span"
            sx={{ fontWeight: 700, fontSize: "0.95rem", color: "primary.main" }}
          >
            {label}
          </Typography>
        </Box>
        <Typography
          variant="body1"
          color="text.primary"
          sx={{ fontWeight: 700 }}
        >
          {value}
        </Typography>
      </Box>
    </Box>
  );
}
