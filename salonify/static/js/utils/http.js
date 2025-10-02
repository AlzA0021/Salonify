// salonify: utils/http.js
export function getCookie(name){
  return document.cookie
    .split(';')
    .map(c => c.trim())
    .find(c => c.startsWith(name + '='))?.split('=')[1] || '';
}
export function csrfToken(){
  return decodeURIComponent(getCookie('csrftoken') || '');
}
export async function csrfFetch(url, options = {}){
  const headers = new Headers(options.headers || {});
  if (!headers.has('X-CSRFToken')) headers.set('X-CSRFToken', csrfToken());
  return fetch(url, { credentials: 'same-origin', ...options, headers });
}
