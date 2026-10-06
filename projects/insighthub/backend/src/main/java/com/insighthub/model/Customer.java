package com.insighthub.model;

import jakarta.persistence.*;

@Entity
@Table(name = "customers")
public class Customer {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    public String name, segment;
    public Double churnRisk;

    public Customer() {}
    public Customer(String name, String segment, Double churnRisk) {
        this.name = name; this.segment = segment; this.churnRisk = churnRisk;
    }
}
