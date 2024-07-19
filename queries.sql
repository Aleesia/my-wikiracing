SELECT TOP 5 articles_links_to_them FROM (COUNT parent_page GROUP BY curr_page ORDER BY num_links_to_page);

SELECT (page_1, page2) AS (parent, child) FROM wikipages WHERE page_2 IS NOT NONE
SELECT (page_2, page3) FROM wikipages WHERE page_3 IS NOT NONE
SELECT (page_3, page4) FROM wikipages WHERE page_4 IS NOT NONE
SELECT (page_4, page5) FROM wikipages WHERE page_5 IS NOT NONE

  
SELECT TOP 5 articles_with_out_links

SELECT (page_1, page2) AS (parent, child) FROM wikipages WHERE page_2 IS NOT NONE
SELECT (page_2, page3) FROM wikipages WHERE page_3 IS NOT NONE
SELECT (page_3, page4) FROM wikipages WHERE page_4 IS NOT NONE
SELECT (page_4, page5) FROM wikipages WHERE page_5 IS NOT NONE
