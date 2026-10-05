package com.insighthub.model;

import jakarta.persistence.*;
import java.time.LocalDate;

@Entity
@Table(name = "sales_records")
public class SalesRecord {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    public String orderId;
    public LocalDate orderDate;
    public String region, country, category, product, channel;
    public Integer units;
    public Double revenue, profit;
    public Long customerId;
}
