// Простий клієнтський helper для роботи з авторизацією.
// Дані лежать у sessionStorage, тому очищаються після закриття вкладки/браузера.
const Auth = {
  // JWT потрібен для Authorization-заголовка у запитах до API.
  setToken(token) { sessionStorage.setItem('token', token); },
  getToken()      { return sessionStorage.getItem('token'); },

  // Короткий профіль користувача зберігаємо для перевірки ролі на сторінках.
  setUser(user)   { sessionStorage.setItem('user', JSON.stringify(user)); },
  getUser()       { return JSON.parse(sessionStorage.getItem('user') || 'null'); },
  isLoggedIn()    { return !!this.getToken(); },
  logout()        { sessionStorage.clear(); window.location = '/index.html'; }
};
