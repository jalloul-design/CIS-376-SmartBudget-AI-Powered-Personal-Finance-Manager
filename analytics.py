from datetime import datetime
from collections import defaultdict


class AnalyticsEngine:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_transactions(self, month=None, year=None):
        cursor = self.db.cursor()
        if month and year:
            cursor.execute(
                "SELECT * FROM transactions WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?",
                (str(month).zfill(2), str(year))
            )
        else:
            cursor.execute("SELECT * FROM transactions")
        return cursor.fetchall()

    def total_income(self, month=None, year=None):
        transactions = self.get_transactions(month, year)
        return round(sum(t["amount"] for t in transactions if t["amount"] > 0), 2)

    def total_expenses(self, month=None, year=None):
        transactions = self.get_transactions(month, year)
        return round(sum(abs(t["amount"]) for t in transactions if t["amount"] < 0), 2)

    def savings_rate(self, month=None, year=None):
        income = self.total_income(month, year)
        expenses = self.total_expenses(month, year)
        if income == 0:
            return 0.0
        return round(((income - expenses) / income) * 100, 2)

    def average_daily_spending(self, month=None, year=None):
        transactions = self.get_transactions(month, year)
        expenses = [t for t in transactions if t["amount"] < 0]
        if not expenses:
            return 0.0
        dates = set(t[3] for t in expenses)
        total = sum(abs(t["amount"]) for t in expenses)
        return round(total / len(dates), 2)

    def spending_by_category(self, month=None, year=None):
        transactions = self.get_transactions(month, year)
        category_totals = defaultdict(float)
        for t in transactions:
            if t["amount"] < 0:
                category_totals[t[4]] += abs(t["amount"])
        return {k: round(v, 2) for k, v in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)}

    def top_expense_categories(self, month=None, year=None, top_n=3):
        by_category = self.spending_by_category(month, year)
        return list(by_category.items())[:top_n]

    def period_comparison(self, month, year):
        """Compare current month spending vs previous month."""
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        current = self.spending_by_category(month, year)
        previous = self.spending_by_category(prev_month, prev_year)
        comparison = {}
        all_categories = set(list(current.keys()) + list(previous.keys()))
        for cat in all_categories:
            curr_val = current.get(cat, 0)
            prev_val = previous.get(cat, 0)
            if prev_val > 0:
                pct_change = round(((curr_val - prev_val) / prev_val) * 100, 1)
            else:
                pct_change = 100.0 if curr_val > 0 else 0.0
            comparison[cat] = {
                "current": curr_val,
                "previous": prev_val,
                "pct_change": pct_change
            }
        return comparison


class ReportGenerator:
    def __init__(self, analytics_engine):
        self.engine = analytics_engine

    def generate_monthly_report(self, month, year):
        month_name = datetime(year, month, 1).strftime("%B %Y")
        income = self.engine.total_income(month, year)
        expenses = self.engine.total_expenses(month, year)
        savings = round(income - expenses, 2)
        savings_rate = self.engine.savings_rate(month, year)
        avg_daily = self.engine.average_daily_spending(month, year)
        top_categories = self.engine.top_expense_categories(month, year)
        comparison = self.engine.period_comparison(month, year)
        recommendations = self._generate_recommendations(
            comparison, savings_rate)

        report = {
            "month": month_name,
            "total_income": income,
            "total_expenses": expenses,
            "net_savings": savings,
            "savings_rate_pct": savings_rate,
            "avg_daily_spending": avg_daily,
            "top_categories": top_categories,
            "period_comparison": comparison,
            "recommendations": recommendations
        }
        return report

    def _generate_recommendations(self, comparison, savings_rate):
        recommendations = []
        for category, data in comparison.items():
            if data["pct_change"] >= 20:
                recommendations.append(
                    f"You spent {data['pct_change']}% more on {category} vs last month (${data['current']} vs ${data['previous']})."
                )
            elif data["pct_change"] <= -20:
                recommendations.append(
                    f"Great job! You reduced {category} spending by {abs(data['pct_change'])}% compared to last month."
                )
        if savings_rate < 10:
            recommendations.append(
                "Your savings rate is below 10%. Try reducing discretionary spending.")
        elif savings_rate >= 20:
            recommendations.append(
                f"Excellent! You saved {savings_rate}% of your income this month.")
        if not recommendations:
            recommendations.append(
                "Your spending looks consistent with last month. Keep it up!")
        return recommendations

    def format_report_text(self, report):
        lines = [
            f"=== Monthly Report: {report['month']} ===",
            f"Total Income:       ${report['total_income']}",
            f"Total Expenses:     ${report['total_expenses']}",
            f"Net Savings:        ${report['net_savings']}",
            f"Savings Rate:       {report['savings_rate_pct']}%",
            f"Avg Daily Spending: ${report['avg_daily_spending']}",
            "",
            "Top Spending Categories:",
        ]
        for cat, amount in report["top_categories"]:
            lines.append(f"  - {cat}: ${amount}")
        lines.append("")
        lines.append("Recommendations:")
        for rec in report["recommendations"]:
            lines.append(f"  * {rec}")
        return "\n".join(lines)
