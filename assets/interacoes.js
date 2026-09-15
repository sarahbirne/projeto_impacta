function toggleCols(btn){
  var t=document.getElementById(btn.dataset.table);
  var oculto=t.classList.toggle('col-hide');
  btn.setAttribute('aria-expanded', oculto ? 'false':'true');
  btn.textContent = oculto ? 'Ver distribuição das notas' : 'Ocultar distribuição das notas';
}
function toggleAll(btn){
  var list=document.getElementById(btn.dataset.list);
  var items=list.querySelectorAll('details.cmt');
  var open=btn.textContent.indexOf('Expandir')===0;
  items.forEach(function(x){ x.open=open; });
  btn.textContent = open ? 'Recolher todos' : 'Expandir todos';
}
function showCsm(id){
  var wrap=document.getElementById(id).parentNode;
  wrap.querySelectorAll('.side-panel').forEach(function(p){ p.hidden = (p.id!==id); });
  wrap.parentNode.querySelectorAll('.side-nav button').forEach(function(b){
    b.setAttribute('aria-selected', b.getAttribute('aria-controls')===id ? 'true':'false');
  });
}
function showTab(id){
  var ids=['t1','t2','t3'];
  ids.forEach(function(t){
    document.getElementById(t).hidden = (t!==id);
    document.getElementById('tab-'+t).setAttribute('aria-selected', t===id ? 'true':'false');
  });
}
