function post(uri, params){
    var form = document.createElement('form');
    
    form.setAttribute('method','POST');
    form.setAttribute('action', uri);
    
    
    if (params instanceof Array){
        for (var item=0; item < params.length; item++){
            var input = document.createElement('input');
            input.setAttribute('type','text');
            switch(item){
                case 0:
                    input.setAttribute('name','userTokenId');
                    break;
                case 1: 
                    input.setAttribute('name','fTokenId');
                    break;
                default:
                    break;
            }
            input.setAttribute('value',params[item])
            form.insertAdjacentElement('beforeend',input);
        }
        
    } else {
        var input = document.createElement('input');
        input.setAttribute('type','text');
        input.setAttribute('name','userTokenId');
        input.setAttribute('value', params);
            
        form.insertAdjacentElement('beforeend', input);
    }
    
    form.submit();
} 

function storageAvailable(type){ 
    try {
		var storage = window[type],
			x = '__storage_test__';
		storage.setItem(x, x);
		storage.removeItem(x);
		return true;
	}
	catch(e) {
		return false;
	}
}

function testUUID(uuid){
    uuid_valid = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$/;
    return uuid_valid.test(uuid);
}