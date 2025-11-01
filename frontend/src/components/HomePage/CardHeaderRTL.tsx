import { Box, Typography } from "@mui/material";
import type { SxProps } from "@mui/material";

export default function CardHeaderRTL({
  title,
  icon,
  sx,
}: {
  title: string;
  icon: React.ReactNode;
  sx?: SxProps;
}) {
  return (
    <Box
      sx={{
        width: "100%", // חשוב: גורם ל-flex-end להצמיד לימין הכרטיס
        direction: "rtl", // מוודא סדר RTL ברמת הכותרת
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-start",
        gap: 1,
        mb: 1,
        ...sx,
      }}
    >
      {icon}
      <Typography variant="h6" sx={{ fontWeight: 700, textAlign: "right" }}>
        {title}
      </Typography>
    </Box>
  );
}
