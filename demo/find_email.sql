    SELECT email AS mail
      FROM contact_info
INNER JOIN client_name
        ON contact_info.user_id = client_name.user_id
     WHERE last_name = '${last_name}';
