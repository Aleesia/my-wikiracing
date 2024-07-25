-- top 5 що мають найбільшу кількість посилань на себе
SELECT child AS page, count(child) as count_links
FROM wikipages
GROUP BY child
ORDER BY count_links DESC
FETCH FIRST 5 ROWS ONLY;
  
-- top 5  з найбільшою кількістю посилань на інші статті
SELECT parent AS page, count(parent) as count_links
FROM wikipages
GROUP BY parent
ORDER BY count_links DESC
FETCH FIRST 5 ROWS ONLY;
