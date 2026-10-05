package com.insighthub.controller;

import com.insighthub.model.SalesRecord;
import com.insighthub.repository.SalesRecordRepository;
import com.insighthub.service.AnalyticsService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/sales")
public class SalesController {
    private final SalesRecordRepository repo;
    private final AnalyticsService analytics;

    public SalesController(SalesRecordRepository repo, AnalyticsService analytics) {
        this.repo = repo; this.analytics = analytics;
    }

    @GetMapping
    public Map<String, Object> list(@RequestParam(defaultValue = "") String region,
                                    @RequestParam(defaultValue = "") String category,
                                    @RequestParam(defaultValue = "") String channel,
                                    @RequestParam(defaultValue = "") String q,
                                    @RequestParam(defaultValue = "0") int page,
                                    @RequestParam(defaultValue = "15") int size) {
        Page<SalesRecord> p = repo.search(region, category, channel, q.trim(), PageRequest.of(page, size));
        return Map.of("items", p.getContent(), "total", p.getTotalElements(), "page", page, "pages", p.getTotalPages());
    }

    @GetMapping("/filters")
    public Map<String, Object> filters() { return analytics.filters(); }
}
