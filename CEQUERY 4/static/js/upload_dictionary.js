 $('#holder').on({
      'dragover dragenter': function(e) {
          e.preventDefault();
          e.stopPropagation();
      },
      'drop': function(e) {
          //console.log(e.originalEvent instanceof DragEvent);
          var dataTransfer =  e.originalEvent.dataTransfer;
          if( dataTransfer && dataTransfer.files.length) {
              e.preventDefault();
              e.stopPropagation();
              $.each( dataTransfer.files, function(i, file) {
                var reader = new FileReader();
                reader.onload = $.proxy(function(file, $fileList, event) {
                  var img = file.type.match('image.*') ? "<img src='" + event.target.result + "' /> " : "";
                  $fileList.prepend( $("<li>").append( img + file.name ) );
                }, this, file, $("#fileList"));
                reader.readAsDataURL(file);
              });
          }
      }
  });
 function showMe (box) {

    var chboxs = document.getElementsByName("myselect");
    var vis = "none";
    if(box=='Yes'){
      document.getElementById("noti").checked = false;
       document.getElementById("No").style.display = "none";
    }
    if(box=='No'){
      document.getElementById("yesti").checked = false;
       document.getElementById("Yes").style.display = "none";
    }
    for(var i=0;i<chboxs.length;i++) {
        if(chboxs[i].checked){
         vis = "block";
            break;
        }
    }
    document.getElementById(box).style.display = vis;


  }