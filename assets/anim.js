/* ═══ camada de animação — aditiva; nunca altera valores nem estrutura ═══ */
(function(){
  if(!('IntersectionObserver' in window))return;
  document.documentElement.classList.add('anim-on');

  /* 1. guarda os alvos das barras e zera o estado inicial */
  document.querySelectorAll('.bar-row .bf').forEach(function(el){
    el.dataset.w=el.style.width; el.style.width='0%';
  });
  document.querySelectorAll('.cc-bar').forEach(function(el){
    el.dataset.h=el.style.height; el.style.height='0%';
  });

  /* 2. marca o que entra com scroll reveal */
  var alvos=['.section-title','.sub-title','.q-title','.section-note','.kpi-card',
             '.csm-picto-card','.funil-wrap','.pie-wrap','.cloud-wrap','.cc-wrap',
             '.cc-legend','.callout','.cmt-group','.tabs','.side-tabs',
             '.col-toggle-wrap','.doc-footer','.toc','p.src','table'].join(',');
  document.querySelectorAll(alvos).forEach(function(el){el.classList.add('rv');});

  /* atraso escalonado dentro de cada grupo de cards e de barras */
  function escalonar(container,filho){
    document.querySelectorAll(container).forEach(function(g){
      g.querySelectorAll(filho).forEach(function(el,i){el.dataset.i=i;});
    });
  }
  escalonar('.kpi-grid','.kpi-card');
  escalonar('.csm-picto-grid','.csm-picto-card');
  var n=0;
  document.querySelectorAll('.bar-row').forEach(function(el){
    el.classList.add('rv');
    var ant=el.previousElementSibling;
    n=(ant&&ant.classList.contains('bar-row'))?n+1:0;
    el.dataset.i=n;
  });

  /* 3. contagem crescente, terminando exatamente no texto original */
  function contar(el){
    if(el.dataset.contou)return; el.dataset.contou='1';
    var alvo=el.textContent, m=alvo.match(/-?\d+(?:,\d+)?/);
    if(!m)return;
    var bruto=m[0], casas=(bruto.split(',')[1]||'').length,
        fim=parseFloat(bruto.replace(',','.')),
        antes=alvo.slice(0,m.index), depois=alvo.slice(m.index+bruto.length),
        dur=900, ini=performance.now();
    (function passo(t){
      var p=Math.min(((t||ini)-ini)/dur,1), e=1-Math.pow(1-p,3);
      if(p<1){
        el.textContent=antes+(fim*e).toFixed(casas).replace('.',',')+depois;
        requestAnimationFrame(passo);
      }else{ el.textContent=alvo; }
    })(ini);
  }

  /* 4. revela um elemento: classe .in, barra no tamanho final e contagem */
  function revelar(el,atraso){
    if(el.classList.contains('in'))return;
    setTimeout(function(){
      el.classList.add('in');
      var bf=el.querySelector&&el.querySelector('.bf');
      if(bf&&bf.dataset.w)bf.style.width=bf.dataset.w;
      if(el.querySelectorAll)el.querySelectorAll('.kpi-value').forEach(contar);
    },atraso||0);
  }

  var obs=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting)return;
      obs.unobserve(e.target);
      revelar(e.target,(+e.target.dataset.i||0)*70);
    });
  },{threshold:.12,rootMargin:'0px 0px -40px 0px'});
  document.querySelectorAll('.rv').forEach(function(el){obs.observe(el);});

  /* 5. gráficos em SVG: cascata nas etapas, fatias e bolhas */
  function cascata(sel,filhos,passo){
    var o=new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(!e.isIntersecting)return;
        o.unobserve(e.target);
        e.target.querySelectorAll(filhos).forEach(function(f,i){
          f.style.animationDelay=(i*passo)+'ms';
        });
        e.target.classList.add('in');
      });
    },{threshold:.2});
    document.querySelectorAll(sel).forEach(function(el){o.observe(el);});
  }
  cascata('svg.funil','path',110);
  cascata('svg.funil','text',90);
  cascata('svg.pie','path',150);
  cascata('svg.cloud','g',55);

  var ccObs=new IntersectionObserver(function(es){
    es.forEach(function(e){
      if(!e.isIntersecting)return;
      ccObs.unobserve(e.target);
      e.target.querySelectorAll('.cc-group').forEach(function(g,gi){
        g.classList.add('in');
        g.querySelectorAll('.cc-bar').forEach(function(b,bi){
          setTimeout(function(){if(b.dataset.h)b.style.height=b.dataset.h;},gi*90+bi*60);
        });
      });
    });
  },{threshold:.18});
  document.querySelectorAll('.cc-chart').forEach(function(el){ccObs.observe(el);});

  /* 6. rede de segurança: conteúdo que estava oculto (aba fechada, bloco recolhido)
        é revelado na hora em que aparece, sem depender do observador */
  function revelarEscopo(raiz){
    if(!raiz||!raiz.querySelectorAll)return;
    raiz.querySelectorAll('.rv').forEach(function(el){revelar(el,(+el.dataset.i||0)*60);});
    raiz.querySelectorAll('svg.funil,svg.pie,svg.cloud').forEach(function(s){s.classList.add('in');});
    raiz.querySelectorAll('.cc-group').forEach(function(g){g.classList.add('in');});
    raiz.querySelectorAll('.cc-bar').forEach(function(b){if(b.dataset.h)b.style.height=b.dataset.h;});
  }
  document.addEventListener('click',function(ev){
    var b=ev.target.closest&&ev.target.closest('.tabs button,.side-nav button');
    if(!b)return;
    setTimeout(function(){
      var id=b.getAttribute('aria-controls');
      if(id)revelarEscopo(document.getElementById(id));
    },30);
  });
  document.querySelectorAll('details').forEach(function(d){
    d.addEventListener('toggle',function(){ if(d.open)revelarEscopo(d); });
  });

  /* 7. voltar ao topo */
  var btn=document.createElement('button');
  btn.id='toTop'; btn.type='button'; btn.innerHTML='&uarr;';
  btn.setAttribute('aria-label','Voltar ao topo');
  btn.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};
  document.body.appendChild(btn);
  window.addEventListener('scroll',function(){
    btn.classList.toggle('show',window.scrollY>500);
  },{passive:true});
})();
