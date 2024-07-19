SELECT TOP 5 articles_links_to_them FROM (COUNT parent_page GROUP BY curr_page ORDER BY num_links_to_page);

SELECT TOP 5 
