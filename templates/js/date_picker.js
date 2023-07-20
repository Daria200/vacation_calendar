function() {
    $('#picker').datetimepicker({
        defaultDate: "11/1/2013",
       disabledDates: [
           moment("12/26/2013"),
           new Date(2013, 11 - 1, 12),
           "11/13/2013 00:53"
       ]
    });}