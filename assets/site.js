(function(){
  var m=document.getElementById('bci'),k='sarfaesi_bci_ok';
  var ok=false;try{ok=localStorage.getItem(k)==='1'}catch(e){}
  if(!ok&&m){m.hidden=false;document.body.style.overflow='hidden';
    document.getElementById('bci-agree').onclick=function(){
      m.hidden=true;document.body.style.overflow='';
      try{localStorage.setItem(k,'1')}catch(e){}
    };}
})();
