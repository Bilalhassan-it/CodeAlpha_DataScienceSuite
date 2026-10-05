package com.insighthub.model;

import jakarta.persistence.*;

@Entity
@Table(name = "products")
public class Product {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    public String name, category;
    public Double price;

    public Product() {}
    public Product(String name, String category, double price) {
        this.name = name; this.category = category; this.price = price;
    }
}
