import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  Divider,
} from "@mui/material";
import { ChildCare } from "@mui/icons-material";

interface FetalDevelopmentInfo {
  week: number;
  title: string;
  description: string;
}

interface FetalDevelopmentCardProps {
  currentPregnancyWeek?: number;
}

function FetalDevelopmentCard({
  currentPregnancyWeek,
}: FetalDevelopmentCardProps) {
  const [fetalInfo, setFetalInfo] = useState<FetalDevelopmentInfo | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadFetalDevelopmentInfo = async () => {
      if (!currentPregnancyWeek) return;

      setLoading(true);
      try {
        const response = await fetch("/data/fetal-development.json");
        if (response.ok) {
          const data = await response.json();
          const weekInfo = data.find(
            (item: FetalDevelopmentInfo) => item.week === currentPregnancyWeek
          );
          setFetalInfo(weekInfo || null);
        }
      } catch (error) {
        console.error("Failed to load fetal development info:", error);
      } finally {
        setLoading(false);
      }
    };

    loadFetalDevelopmentInfo();
  }, [currentPregnancyWeek]);

  if (!currentPregnancyWeek || loading || !fetalInfo) return null;

  return (
    <Card
      sx={{
        mb: 3,
        borderRadius: 3,
        background:
          "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%)",
        border: "1px solid rgba(233, 30, 99, 0.12)",
        boxShadow: "0 8px 24px rgba(233, 30, 99, 0.08)",
        backdropFilter: "blur(6px)",
        overflow: "hidden",
      }}
    >
      {/* פס עליון תואם למותג */}
      <Box
        sx={{
          height: 6,
          width: "100%",
          background:
            "linear-gradient(90deg, rgba(233,30,99,0.45), rgba(156,39,176,0.45))",
        }}
      />

      <CardContent sx={{ p: { xs: 2.5, md: 3 }, direction: "rtl" }}>
        {/* כותרת + אייקון + שבב שבוע */}
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            justifyContent: "space-between",
            mb: 1.5,
          }}
        >
          {/* אייקון בתוך עיגול עדין */}
          <Box
            sx={{
              width: 42,
              height: 42,
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              backgroundColor: "rgba(233,30,99,0.10)",
              border: "1px solid rgba(233,30,99,0.22)",
              flexShrink: 0,
            }}
          >
            <ChildCare sx={{ fontSize: 24, color: "primary.main" }} />
          </Box>

          {/* כותרת ממורכזת עם גרדיאנט טקסט עדין */}
          <Box sx={{ flex: 1, textAlign: "center" }}>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 800,
                mb: 0.75,
                background: "linear-gradient(45deg, #e91e63, #9c27b0)",
                backgroundClip: "text",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              {fetalInfo.title}
            </Typography>

            {/* פס דקורטיבי קצר */}
            <Box
              sx={{
                width: 64,
                height: 4,
                mx: "auto",
                borderRadius: 2,
                background:
                  "linear-gradient(90deg, rgba(233,30,99,0.55), rgba(156,39,176,0.45))",
              }}
            />

            {/* שבב שבוע עדין */}
            <Chip
              label={`שבוע ${fetalInfo.week}`}
              size="small"
              variant="outlined"
              color="primary"
              sx={{
                mt: 1,
                fontWeight: 500,
                bgcolor: "rgba(233,30,99,0.06)",
                borderColor: "rgba(233,30,99,0.25)",
              }}
            />
          </Box>

          {/* מרווח סימטרי לצד שמאל */}
          <Box sx={{ width: 42, height: 42, visibility: "hidden" }} />
        </Box>

        <Divider sx={{ borderColor: "rgba(233,30,99,0.15)", mb: 2 }} />

        {/* טקסט קריא ונעים */}
        <Box sx={{ maxWidth: 980, mx: "auto" }}>
          <Typography
            variant="body1"
            color="text.secondary"
            sx={{
              textAlign: "right",
              lineHeight: 1.9,
              fontSize: { xs: "1.02rem", md: "1.08rem" },
              letterSpacing: 0.1,
              whiteSpace: "pre-line",
            }}
          >
            {fetalInfo.description}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

export default FetalDevelopmentCard;
