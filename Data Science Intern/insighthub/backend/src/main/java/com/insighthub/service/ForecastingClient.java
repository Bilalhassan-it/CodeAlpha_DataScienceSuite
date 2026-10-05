package com.insighthub.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

/** Calls the Python FastAPI analytics service. */
@Service
public class ForecastingClient {
    private final RestTemplate rest = new RestTemplate();
    @Value("${analytics.url:http://localhost:8000}")
    private String baseUrl;

    @SuppressWarnings("unchecked")
    public Map<String, Object> forecast(List<Map<String, Object>> series, int periods) {
        return rest.postForObject(baseUrl + "/forecast", Map.of("series", series, "periods", periods), Map.class);
    }
}
