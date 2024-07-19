-- top 5 що мають найбільшу кількість посилань на себе

SELECT child, count(child) as num_links_to
  FROM  
((SELECT page_1 AS parent, page_2 AS child FROM wikipages WHERE (page_2 IS NOT NONE AND page_3 IS NONE))
  UNION
(SELECT page_2 AS parent, page_3 AS child FROM wikipages WHERE (page_3 IS NOT NONE AND page_4 IS NONE))
  UNION
(SELECT page_3 AS parent, page_4 AS child FROM wikipages WHERE (page_4 IS NOT NONE AND page_5 IS NONE))
  UNION
(SELECT page_4 AS parent, page_5 AS child FROM wikipages WHERE page_5 IS NOT NONE))
 GROUP by child
  ORDER BY num_links_to DESC
  
-- top 5  з найбільшою кількістю посилань на інші статті
SELECT parent, count(parent) as num_links_from
  FROM  
((SELECT page_1 AS parent, page_2 AS child FROM wikipages WHERE (page_2 IS NOT NONE AND page_3 IS NONE))
  UNION
(SELECT page_2 AS parent, page_3 AS child FROM wikipages WHERE (page_3 IS NOT NONE AND page_4 IS NONE))
  UNION
(SELECT page_3 AS parent, page_4 AS child FROM wikipages WHERE (page_4 IS NOT NONE AND page_5 IS NONE))
  UNION
(SELECT page_4 AS parent, page_5 AS child FROM wikipages WHERE page_5 IS NOT NONE))
 GROUP by parent
  ORDER BY num_links_from DESC
