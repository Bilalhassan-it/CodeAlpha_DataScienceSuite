package com.insighthub.config;

import com.insighthub.model.*;
import com.insighthub.repository.*;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.*;

/** Fills the H2 database with ~6000 demo orders on first start. */
@Component
public class DataSeeder implements CommandLineRunner {
    private final SalesRecordRepository sales;
    private final CustomerRepository customers;
    private final ProductRepository products;

    public DataSeeder(SalesRecordRepository s, CustomerRepository c, ProductRepository p) {
        this.sales = s; this.customers = c; this.products = p;
    }

    private static double r2(double v) { return Math.round(v * 100) / 100.0; }

    @Override
    public void run(String... args) {
        if (sales.count() > 0) return;
        Random r = new Random(42);
        String[][] cats = {
            {"Electronics", "Laptop Pro", "Smart Watch", "Wireless Earbuds", "4K Monitor"},
            {"Software", "Analytics Suite", "Cloud Backup", "Security Pro"},
            {"Office", "Ergo Chair", "Standing Desk", "Desk Lamp"},
            {"Accessories", "USB-C Hub", "Laptop Sleeve", "Webcam HD"}};
        Map<String, String[]> geo = new LinkedHashMap<>();
        geo.put("North America", new String[]{"USA", "Canada", "Mexico"});
        geo.put("Europe", new String[]{"Germany", "UK", "France", "Spain"});
        geo.put("Asia Pacific", new String[]{"Pakistan", "India", "Japan", "Australia"});
        geo.put("Middle East", new String[]{"UAE", "Saudi Arabia", "Turkey"});
        geo.put("Latin America", new String[]{"Brazil", "Argentina", "Chile"});
        String[] regions = geo.keySet().toArray(new String[0]);
        String[] channels = {"Online", "Retail", "Partner", "Direct"};
        String[] segments = {"Enterprise", "SMB", "Startup", "Consumer"};

        List<Product> pl = new ArrayList<>();
        for (String[] c : cats)
            for (int i = 1; i < c.length; i++) pl.add(new Product(c[i], c[0], 20 + r.nextInt(480)));
        products.saveAll(pl);

        List<Customer> cl = new ArrayList<>();
        for (int i = 1; i <= 300; i++)
            cl.add(new Customer("Customer " + i, segments[r.nextInt(segments.length)], r2(r.nextDouble())));
        customers.saveAll(cl);

        LocalDate start = LocalDate.now().minusMonths(24).withDayOfMonth(1);
        long span = ChronoUnit.DAYS.between(start, LocalDate.now()) + 1;
        List<SalesRecord> out = new ArrayList<>();
        for (int i = 0; i < 6000; i++) {
            SalesRecord s = new SalesRecord();
            long off = r.nextInt((int) span);
            s.orderDate = start.plusDays(off);
            s.orderId = "ORD-" + (10000 + i);
            s.region = regions[r.nextInt(regions.length)];
            String[] cs = geo.get(s.region);
            s.country = cs[r.nextInt(cs.length)];
            Product p = pl.get(r.nextInt(pl.size()));
            s.category = p.category; s.product = p.name;
            s.channel = channels[r.nextInt(channels.length)];
            s.units = 1 + r.nextInt(20);
            double growth = 1 + off / (span * 2.0);
            double season = 1 + 0.2 * Math.sin(s.orderDate.getMonthValue() * Math.PI / 6);
            s.revenue = r2(s.units * p.price * (0.9 + 0.2 * r.nextDouble()) * growth * season);
            s.profit = r2(s.revenue * (0.15 + 0.25 * r.nextDouble()));
            s.customerId = cl.get(r.nextInt(cl.size())).id;
            out.add(s);
        }
        sales.saveAll(out);
        System.out.println("InsightHub: seeded " + out.size() + " orders");
    }
}
