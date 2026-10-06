package com.insighthub.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/** Read-only SQL console. */
@RestController
@RequestMapping("/api/query")
public class QueryController {
    private static final String BLOCKED =
        "(?is).*\\b(insert|update|delete|drop|alter|create|truncate|merge|call|grant|revoke|runscript|script|shutdown)\\b.*";
    private final JdbcTemplate jdbc;

    public QueryController(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @PostMapping
    public ResponseEntity<?> run(@RequestBody Map<String, String> body) {
        String sql = body.getOrDefault("sql", "").trim().replaceAll(";+\\s*$", "");
        String low = sql.toLowerCase();
        if (!(low.startsWith("select") || low.startsWith("with")) || sql.contains(";") || sql.matches(BLOCKED))
            return ResponseEntity.badRequest().body(Map.of("error", "Only single read-only SELECT queries are allowed."));
        try {
            long t0 = System.currentTimeMillis();
            List<String> cols = new ArrayList<>();
            List<List<Object>> rows = new ArrayList<>();
            jdbc.query("SELECT * FROM (" + sql + ") LIMIT 500", rs -> {
                int n = rs.getMetaData().getColumnCount();
                for (int i = 1; i <= n; i++) cols.add(rs.getMetaData().getColumnLabel(i).toLowerCase());
                while (rs.next()) {
                    List<Object> row = new ArrayList<>();
                    for (int i = 1; i <= n; i++) row.add(rs.getObject(i) == null ? null : rs.getObject(i).toString());
                    rows.add(row);
                }
                return null;
            });
            return ResponseEntity.ok(Map.of("columns", cols, "rows", rows, "ms", System.currentTimeMillis() - t0));
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("error", String.valueOf(e.getMessage())));
        }
    }
}
