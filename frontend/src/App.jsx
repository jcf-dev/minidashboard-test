import { useEffect, useMemo, useState } from "react";
import { RefreshCcw, Save } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

const API_URL = import.meta.env.VITE_API_URL ?? "/api/dashboard/";
const API_KEY = import.meta.env.VITE_DASHBOARD_API_KEY ?? "dev-dashboard-key";
const CLIENT_ID = import.meta.env.VITE_CLIENT_ID ?? "1";

const money = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const dayLabel = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
});

function App() {
  const [dashboard, setDashboard] = useState(null);
  const [status, setStatus] = useState("loading");
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(false);
  const [targetDraft, setTargetDraft] = useState("");
  const [saving, setSaving] = useState(false);

  async function loadDashboard() {
    setStatus("loading");
    setError("");

    try {
      const response = await fetch(API_URL, {
        headers: {
          "X-API-Key": API_KEY,
          "X-Client-Id": CLIENT_ID,
        },
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "Dashboard request failed.");
      }

      setDashboard(payload);
      setTargetDraft(String(payload.monthlyGoal));
      setStatus("ready");
    } catch (requestError) {
      setError(requestError.message);
      setStatus("error");
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  async function saveTarget(event) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      const response = await fetch(API_URL, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "X-API-Key": API_KEY,
          "X-Client-Id": CLIENT_ID,
        },
        body: JSON.stringify({ monthlyGoal: Number(targetDraft) }),
      });

      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error ?? "Target update failed.");
      }

      setDashboard(payload);
      setTargetDraft(String(payload.monthlyGoal));
      setEditing(false);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  }

  const chartRows = useMemo(() => {
    if (!dashboard) {
      return [];
    }

    const totals = dashboard.sales.reduce((byDate, sale) => {
      byDate[sale.soldAt] = (byDate[sale.soldAt] ?? 0) + sale.amount;
      return byDate;
    }, {});

    return Object.entries(totals)
      .sort(([left], [right]) => new Date(left) - new Date(right))
      .map(([date, total]) => ({ date, total }));
  }, [dashboard]);

  if (status === "loading") {
    return (
      <main className="mx-auto flex min-h-svh w-full max-w-6xl items-center justify-center px-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Loading dashboard...</CardTitle>
            <CardDescription>Fetching client sales data.</CardDescription>
          </CardHeader>
        </Card>
      </main>
    );
  }

  if (status === "error") {
    return (
      <main className="mx-auto flex min-h-svh w-full max-w-6xl items-center justify-center px-4">
        <Card className="w-full max-w-md border-destructive/40">
          <CardHeader>
            <CardTitle className="text-destructive">Dashboard unavailable</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      </main>
    );
  }

  const target = dashboard.monthlyGoal;
  const total = dashboard.monthlyTotal;
  const remaining = Math.max(target - total, 0);
  const progress = target > 0 ? Math.min((total / target) * 100, 100) : 0;
  const maxChartValue = Math.max(...chartRows.map((row) => row.total), 1);

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-6 sm:px-6 lg:py-10">
      <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase text-muted-foreground">Client dashboard</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-normal text-foreground sm:text-4xl">
            {dashboard.client.name}
          </h1>
          <p className="mt-2 text-sm text-muted-foreground">{dashboard.client.email}</p>
        </div>
        <Button className="w-full sm:w-auto" onClick={loadDashboard}>
          <RefreshCcw data-icon="inline-start" />
          Refresh
        </Button>
      </header>

      <section className="mb-5 grid gap-4 md:grid-cols-3" aria-label="Monthly metrics">
        <Card>
          <CardHeader>
            <CardDescription>Monthly sales</CardDescription>
            <CardTitle className="text-3xl">{money.format(total)}</CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={progress} aria-label={`${Math.round(progress)}% of target`} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-col gap-4 space-y-0 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <CardDescription>Monthly goal</CardDescription>
              {editing ? (
                <form
                  className="mt-2 grid gap-2 sm:grid-cols-[minmax(120px,1fr)_auto_auto]"
                  onSubmit={saveTarget}
                >
                  <Input
                    aria-label="Monthly goal"
                    min="0"
                    step="100"
                    type="number"
                    value={targetDraft}
                    onChange={(event) => setTargetDraft(event.target.value)}
                  />
                  <Button type="submit" disabled={saving}>
                    <Save data-icon="inline-start" />
                    {saving ? "Saving" : "Save"}
                  </Button>
                  <Button
                    variant="outline"
                    type="button"
                    onClick={() => {
                      setTargetDraft(String(dashboard.monthlyGoal));
                      setEditing(false);
                    }}
                  >
                    Cancel
                  </Button>
                </form>
              ) : (
                <CardTitle className="mt-1 text-3xl">{money.format(target)}</CardTitle>
              )}
            </div>
            {!editing && (
              <Button variant="outline" onClick={() => setEditing(true)}>
                Edit Target
              </Button>
            )}
          </CardHeader>
        </Card>

        <Card>
          <CardHeader>
            <CardDescription>Remaining</CardDescription>
            <CardTitle className="text-3xl">{money.format(remaining)}</CardTitle>
            <CardDescription>{Math.round(progress)}% of goal reached</CardDescription>
          </CardHeader>
        </Card>
      </section>

      {error && (
        <div className="mb-5 rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <section className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Sales by Date</CardTitle>
            <CardDescription>{chartRows.length} days</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3" aria-label="Sales by date">
            {chartRows.map((row) => (
              <div className="grid grid-cols-[4rem_minmax(4rem,1fr)_5rem] items-center gap-3" key={row.date}>
                <span className="text-sm text-muted-foreground">
                  {dayLabel.format(new Date(`${row.date}T00:00:00`))}
                </span>
                <div className="h-3 overflow-hidden rounded-full bg-secondary">
                  <div
                    className="h-full rounded-full bg-chart-2"
                    style={{ width: `${(row.total / maxChartValue) * 100}%` }}
                  />
                </div>
                <strong className="text-right text-sm">{money.format(row.total)}</strong>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="text-base">Sales</CardTitle>
            <CardDescription>{dashboard.sales.length} records</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Sale</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {dashboard.sales.map((sale) => (
                  <TableRow key={sale.id}>
                    <TableCell className="font-medium">{sale.label}</TableCell>
                    <TableCell>{dayLabel.format(new Date(`${sale.soldAt}T00:00:00`))}</TableCell>
                    <TableCell className="text-right">{money.format(sale.amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </section>
    </main>
  );
}

export default App;
