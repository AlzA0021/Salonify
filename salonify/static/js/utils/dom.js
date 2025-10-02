// salonify: utils/dom.js
export const qs  = (sel, parent=document) => parent.querySelector(sel);
export const qsa = (sel, parent=document) => Array.from(parent.querySelectorAll(sel));
export const on  = (el, ev, fn, opts) => el.addEventListener(ev, fn, opts);

export function delegate(parent, selector, type, handler){
  parent.addEventListener(type, function(e){
    const target = e.target.closest(selector);
    if (target && parent.contains(target)) handler.call(target, e);
  });
}
