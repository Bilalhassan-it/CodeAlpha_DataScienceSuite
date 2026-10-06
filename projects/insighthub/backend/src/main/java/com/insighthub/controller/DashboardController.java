package com.insighthub.controller;

import com.insighthub.repository.SalesRecordRepository;
import com.insighthub.service.AnalyticsService;
import com.insighthub.service.ForecastingClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class DashboardController {
    private final AnalyticsService analytics;
    private final ForecastingClient forecasting;
    private final SalesRecordRepository sales;

    public DashboardController(AnalyticsService a, ForecastingClient f, SalesRecordRepository s) {
        this.analytics = a; this.forecasting = f; this.sales = s;
    }

    @GetMapping("/health")
    public Map<String, Object> health() { return Map.of("status", "UP", "rows", sales.count()); }

    @GetMapping("/dashboard/overview")
    public Map<String, Object> overview(@RequestParam(defaultValue = "90") int days) { return analytics.overview(days); }

    @GetMapping("/forecast")
    public ResponseEntity<?> forecast(@RequestParam(defaultValue = "6") int periods) {
        try {
            return ResponseEntity.ok(forecasting.forecast(analytics.monthlySeries(), periods));
        } catch (Exception e) {
            return ResponseEntity.status(503).body(Map.of("error", "Python analytics service not reachable on :8000"));
        }
    }
}
