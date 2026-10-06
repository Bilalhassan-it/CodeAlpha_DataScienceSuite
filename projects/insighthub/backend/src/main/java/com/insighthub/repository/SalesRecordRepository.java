package com.insighthub.repository;

import com.insighthub.model.SalesRecord;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface SalesRecordRepository extends JpaRepository<SalesRecord, Long> {
    @Query("SELECT s FROM SalesRecord s WHERE (:region = '' OR s.region = :region) " +
           "AND (:category = '' OR s.category = :category) AND (:channel = '' OR s.channel = :channel) " +
           "AND (:q = '' OR LOWER(s.orderId) LIKE LOWER(CONCAT('%', :q, '%')) " +
           "OR LOWER(s.product) LIKE LOWER(CONCAT('%', :q, '%')) " +
           "OR LOWER(s.country) LIKE LOWER(CONCAT('%', :q, '%'))) " +
           "ORDER BY s.orderDate DESC, s.id DESC")
    Page<SalesRecord> search(@Param("region") String region, @Param("category") String category,
                             @Param("channel") String channel, @Param("q") String q, Pageable pageable);
}
