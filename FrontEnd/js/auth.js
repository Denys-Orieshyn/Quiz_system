// Зберігає JWT і дані юзера в пам'яті сесії
const Auth = {
  setToken(token) { sessionStorage.setItem('token', token); },
  getToken()      { return sessionStorage.getItem('token'); },
  setUser(user)   { sessionStorage.setItem('user', JSON.stringify(user)); },
  getUser()       { return JSON.parse(sessionStorage.getItem('user') || 'null'); },
  isLoggedIn()    { return !!this.getToken(); },
  logout()        { sessionStorage.clear(); window.location = '/index.html'; }
};