import { useState, useEffect } from "react";
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Stack,
  Divider,
  Button,
} from "@mui/material";
import { PregnantWoman, Assignment } from "@mui/icons-material";
import { Person, Cake, Height, MonitorWeight } from "@mui/icons-material";
import AccountCircle from "@mui/icons-material/AccountCircle";
import { authService } from "../services/authService";
import { useTasks } from "../hooks/useTasks";
import CompactTaskCard from "./Tasks/CompactTaskCard";
import FetalDevelopmentCard from "./FetalDevelopmentCard";
import CardHeaderRTL from "./HomePage/CardHeaderRTL";
import ProfileFieldRow from "./HomePage/ProfileFieldRow";
import Chat from "@mui/icons-material/Chat";

interface HomeLoggedInProps {
  onNavigate?: (screen: string) => void;
}

function HomeLoggedIn({ onNavigate }: HomeLoggedInProps) {
  const [currentUser, setCurrentUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPregnancyWeek, setCurrentPregnancyWeek] = useState<
    number | undefined
  >(undefined);

  const { tasks, loading: tasksLoading } = useTasks();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const userId = authService.getCurrentUserId();
        if (userId) {
          const response = await fetch(`http://localhost:8000/users/${userId}`);
          const userData = await response.json();
          setCurrentUser(userData);
          setCurrentPregnancyWeek(userData.pregnancy_week);
        }
      } catch (error) {
        console.error("Failed to fetch user data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchUserData();
  }, []);

  const getUpcomingTasks = (tasks: any[], currentWeek?: number) => {
    if (!currentWeek) return [];
    return tasks
      .filter((task) => {
        if (task.status === "completed") return false;
        const startWeek = task.start_week ?? task.pregnancy_week;
        const endWeek = task.end_week ?? task.pregnancy_week ?? startWeek;
        if (!startWeek) return false;
        const isInTaskRange =
          currentWeek >= startWeek && currentWeek <= endWeek;
        const isInUpcomingRange =
          startWeek >= currentWeek && startWeek <= currentWeek + 5;
        return isInTaskRange || isInUpcomingRange;
      })
      .sort((a, b) => {
        const aWeek = a.start_week ?? a.pregnancy_week ?? 0;
        const bWeek = b.start_week ?? b.pregnancy_week ?? 0;
        return aWeek - bWeek;
      })
      .slice(0, 3);
  };

  const upcomingTasks = getUpcomingTasks(tasks, currentPregnancyWeek);

  const handleTaskClick = (task: any) => {
    onNavigate?.("tasks");
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <Box
      dir="rtl"
      sx={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%)",
      }}
    >
      <Container maxWidth="lg" sx={{ py: 4 }}>
        {/* כותרת בעברית עם גרדיאנט עדין */}
        <Typography
          variant="h4"
          gutterBottom
          sx={{
            fontWeight: 700,
            background: "linear-gradient(45deg, #e91e63, #9c27b0)",
            backgroundClip: "text",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            textAlign: "center",
          }}
        >
          ברוכה השבה, {currentUser?.name || "משתמשת"}!
        </Typography>
        <Typography
          variant="body1"
          color="text.secondary"
          paragraph
          sx={{ maxWidth: 820, mx: "auto", textAlign: "center" }}
        >
          העוזרת החכמה שלך כאן כדי ללוות אותך ברוגע ובאהבה לאורך כל ההיריון.
        </Typography>

        {/* מידע שבועי על התפתחות העובר */}
        <FetalDevelopmentCard currentPregnancyWeek={currentPregnancyWeek} />

        {/* כרטיס פרופיל – עיצוב עדין + hover */}
        {currentUser && (
          <Card
            onClick={() => onNavigate?.("profile")}
            sx={{
              mb: 3,
              borderRadius: 3,
              boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
              border: "1px solid rgba(233, 30, 99, 0.08)",
              background: "rgba(255,255,255,0.92)",
              backdropFilter: "blur(6px)",
              transition: "all .2s ease",
              cursor: "pointer",
              "&:hover": {
                boxShadow: "0 10px 24px rgba(233, 30, 99, 0.12)",
                borderColor: "rgba(233, 30, 99, 0.25)",
                transform: "translateY(-2px)",
              },
            }}
          >
            <CardContent sx={{ direction: "rtl" }}>
              <CardHeaderRTL
                title="הפרופיל שלך"
                icon={
                  <AccountCircle sx={{ fontSize: 28, color: "primary.main" }} />
                }
              />
              <Divider sx={{ mb: 2, borderColor: "rgba(233,30,99,0.15)" }} />

              {/* 2x2 grid – שורה ממורכזת: תווית + ערך צמודים */}
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", sm: "auto auto" },
                  justifyContent: "center", // מצמיד את שתי העמודות למרכז
                  columnGap: 3, // ריווח אופקי מבוקר
                  rowGap: 1.25, // ריווח אנכי בין השורות
                  textAlign: "right",
                  alignItems: "center",
                }}
              >
                <ProfileFieldRow
                  icon={<Person sx={{ fontSize: 18, color: "primary.main" }} />}
                  label="שם"
                  value={currentUser?.name || "—"}
                />
                <ProfileFieldRow
                  icon={<Cake sx={{ fontSize: 18, color: "primary.main" }} />}
                  label="גיל"
                  value={
                    typeof currentUser?.age === "number" && currentUser.age > 0
                      ? currentUser.age
                      : "—"
                  }
                />
                <ProfileFieldRow
                  icon={<Height sx={{ fontSize: 18, color: "primary.main" }} />}
                  label="גובה"
                  value={
                    currentUser?.height ? `${currentUser.height} ס״מ` : "—"
                  }
                />
                <ProfileFieldRow
                  icon={
                    <MonitorWeight
                      sx={{ fontSize: 18, color: "primary.main" }}
                    />
                  }
                  label="משקל"
                  value={
                    currentUser?.weight ? `${currentUser.weight} ק״ג` : "—"
                  }
                />
              </Box>
            </CardContent>
          </Card>
        )}

        {/* אזור הכרטיסים – RTL, אפקט hover עדין */}
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
            gap: 3,
          }}
        >
          {/* מטלות הריון */}
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
              border: "1px solid rgba(233, 30, 99, 0.08)",
              background:
                "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%)",
              transition: "all .2s ease",
              "&:hover": {
                boxShadow: "0 10px 24px rgba(233, 30, 99, 0.12)",
                borderColor: "rgba(233, 30, 99, 0.25)",
                transform: "translateY(-2px)",
              },
            }}
          >
            <CardContent sx={{ direction: "rtl" }}>
              <CardHeaderRTL
                title="מטלות הריון"
                icon={
                  <Assignment sx={{ fontSize: 36, color: "primary.main" }} />
                }
              />
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2, textAlign: "right" }}
              >
                קבלי מטלות ותזכורות מותאמות אישית למסע ההיריון שלך.
              </Typography>

              {tasksLoading ? (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ textAlign: "right" }}
                >
                  טוען מטלות...
                </Typography>
              ) : upcomingTasks.length > 0 ? (
                <Box sx={{ display: "flex", justifyContent: "center" }}>
                  <Stack spacing={1} sx={{ width: "100%", maxWidth: "640px" }}>
                    <Typography
                      variant="subtitle2"
                      color="text.secondary"
                      sx={{ mb: 1, textAlign: "center", fontWeight: 600 }}
                    >
                      מטלות קרובות
                    </Typography>
                    {upcomingTasks.map((task) => (
                      <Box
                        key={task.task_id}
                        onClick={() => handleTaskClick(task)}
                        sx={{ cursor: "pointer" }}
                      >
                        <CompactTaskCard task={task} />
                      </Box>
                    ))}
                  </Stack>
                </Box>
              ) : (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ textAlign: "right" }}
                >
                  אין כרגע מטלות קרובות.
                </Typography>
              )}
            </CardContent>
          </Card>

          {/* תמיכת AI */}
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: "0 6px 18px rgba(0,0,0,0.06)",
              border: "1px solid rgba(233, 30, 99, 0.08)",
              background:
                "linear-gradient(180deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.9) 100%)",
              transition: "all .2s ease",
              "&:hover": {
                boxShadow: "0 10px 24px rgba(233, 30, 99, 0.12)",
                borderColor: "rgba(233, 30, 99, 0.25)",
                transform: "translateY(-2px)",
              },
            }}
          >
            <CardContent sx={{ direction: "rtl" }}>
              <CardHeaderRTL
                title="תמיכת AI"
                icon={
                  <PregnantWoman sx={{ fontSize: 36, color: "primary.main" }} />
                }
              />
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ textAlign: "right" }}
              >
                דברי איתי! אני כאן לכל שאלה, תשאלי כל מה שאת רוצה לדעת על
                ההיריון שלך.
              </Typography>

              <Box
                sx={{
                  mt: { xs: 3.5, sm: 5 },
                  display: "flex",
                  justifyContent: "center",
                }}
              >
                <Button
                  variant="contained"
                  startIcon={<Chat sx={{ fontSize: 22 }} />} // RTL – האייקון מימין
                  onClick={() => onNavigate?.("chatbot")}
                  sx={{
                    borderRadius: 999,
                    textTransform: "none",
                    fontWeight: 800,
                    letterSpacing: 0.2,
                    fontSize: { xs: "1rem", sm: "1.05rem" },
                    minWidth: { xs: "72%", sm: 320 },
                    maxWidth: 420,
                    height: 56,
                    px: 3,
                    background: "linear-gradient(45deg, #e91e63, #9c27b0)",
                    color: "#fff",
                    border: "1px solid rgba(255,255,255,0.35)",
                    boxShadow:
                      "0 14px 28px rgba(233,30,99,0.28), 0 6px 12px rgba(156,39,176,0.22)",
                    "& .MuiButton-startIcon": {
                      marginLeft: 1.1,
                      marginRight: 0,
                    },
                    "&:hover": {
                      background: "linear-gradient(45deg, #d81b60, #8e24aa)",
                      boxShadow:
                        "0 18px 34px rgba(233,30,99,0.36), 0 8px 16px rgba(156,39,176,0.28)",
                      transform: "translateY(-2px)",
                    },
                    transition: "all .2s ease",
                  }}
                >
                  להתחלת שיחה
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Box>
  );
}

export default HomeLoggedIn;
