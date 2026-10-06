package com.insighthub.service;

import com.insighthub.model.KpiSummary;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.*;

@Service
public class AnalyticsService {
    private final JdbcTemplate jdbc;

    public AnalyticsService(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    /** Runs SQL and lower-cases column names (H2 returns them upper-case). */
    public List<Map<String, Object>> q(String sql, Object... args) {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Map<String, Object> row : jdbc.queryForList(sql, args)) {
            Map<String, Object> m = new LinkedHashMap<>();
            row.forEach((k, v) -> m.put(k.toLowerCase(), v));
            out.add(m);
        }
        return out;
    }

    private KpiSummary kpi(LocalDate a, LocalDate b) {
        Map<String, Object> m = jdbc.queryForMap(
            "SELECT COALESCE(SUM(revenue),0) R, COALESCE(SUM(profit),0) P, COUNT(*) O, " +
            "COUNT(DISTINCT customer_id) C FROM sales_records WHERE order_date > ? AND order_date <= ?", a, b);
        double r = ((Number) m.get("R")).doubleValue();
        long o = ((Number) m.get("O")).longValue();
        return new KpiSummary(r, ((Number) m.get("P")).doubleValue(), o, o == 0 ? 0 : r / o,
                              ((Number) m.get("C")).longValue());
    }

    private List<Map<String, Object>> group(String col, LocalDate from, int limit) {
        return q("SELECT " + col + " AS label, ROUND(SUM(revenue),2) AS amount FROM sales_records " +
                 "WHERE order_date > ? GROUP BY " + col + " ORDER BY amount DESC" +
                 (limit > 0 ? " LIMIT " + limit : ""), from);
    }

    public Map<String, Object> overview(int days) {
        LocalDate now = LocalDate.now(), from = now.minusDays(days);
        Map<String, Object> o = new LinkedHashMap<>();
        o.put("kpis", kpi(from, now));
        o.put("prev", kpi(now.minusDays(2L * days), from));
        o.put("trend", q("SELECT FORMATDATETIME(order_date,'yyyy-MM') AS period, ROUND(SUM(revenue),2) AS revenue, " +
                         "ROUND(SUM(profit),2) AS profit FROM sales_records WHERE order_date > ? " +
                         "GROUP BY period ORDER BY period", from));
        o.put("category", group("category", from, 0));
        o.put("region", group("region", from, 0));
        o.put("product", group("product", from, 8));
        o.put("channel", group("channel", from, 0));
        o.put("segments", q("SELECT c.segment AS segment, ROUND(SUM(s.revenue),2) AS revenue, " +
                            "COUNT(DISTINCT c.id) AS customers, ROUND(AVG(c.churn_risk),2) AS risk " +
                            "FROM sales_records s JOIN customers c ON s.customer_id = c.id " +
                            "WHERE s.order_date > ? GROUP BY c.segment ORDER BY revenue DESC", from));
        return o;
    }

    public Map<String, Object> filters() {
        Map<String, Object> m = new LinkedHashMap<>();
        for (String c : new String[]{"region", "category", "channel"})
            m.put(c + "s", jdbc.queryForList("SELECT DISTINCT " + c + " FROM sales_records ORDER BY 1", String.class));
        return m;
    }

    /** Monthly revenue series (complete months only) for the forecasting service. */
    public List<Map<String, Object>> monthlySeries() {
        List<Map<String, Object>> out = new ArrayList<>();
        for (Map<String, Object> r : q("SELECT FORMATDATETIME(order_date,'yyyy-MM') AS period, " +
                "ROUND(SUM(revenue),2) AS amount FROM sales_records WHERE order_date < ? " +
                "GROUP BY period ORDER BY period", LocalDate.now().withDayOfMonth(1)))
            out.add(Map.of("period", r.get("period"), "value", r.get("amount")));
        return out;
    }
}
