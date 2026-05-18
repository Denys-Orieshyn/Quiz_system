# Образ frontend-сервісу: статичні HTML/CSS/JS файли віддає Nginx.
FROM nginx:alpine

# Копіюємо frontend у стандартну папку, з якої Nginx віддає статичні файли.
COPY . /usr/share/nginx/html

# Замінюємо стандартну конфігурацію Nginx на конфіг із proxy для `/api`.
COPY nginx.conf /etc/nginx/conf.d/default.conf
