$(document).ready(function () {
    $('.payWithRazorpay').click(function (e) { 
        e.preventDefault();

        var fname = $("[name='fname']").val().trim();
        var lname = $("[name='lname']").val().trim();
        var email = $("[name='email']").val().trim();
        var phone = $("[name='phone']").val().trim();
        var address = $("[name='address']").val().trim();
        var city = $("[name='city']").val().trim();
        var state = $("[name='state']").val().trim();
        var country = $("[name='country']").val().trim();
        var pincode = $("[name='pincode']").val().trim();
        var token = $("[name='csrfmiddlewaretoken']").val();

        if (fname === "" || lname === "" || email === "" || phone === "" || 
            address === "" || city === "" || state === "" || country === "" || pincode === "") {
                
            Swal.fire({
                title: "Alert!",
                text: "All fields are mandatory!",
                icon: "error"
            });
            
            return false; // Stop further execution
        } 
        
        // If all fields are filled, proceed with AJAX request
        $.ajax({
            method: "GET",
            url: "/proceed-to-pay/",
            success: function (response) {
                // console.log(response);
                var options = {
                    "key": "rzp_test_ZstdHmaSavTEcj", // Replace with your Razorpay Key ID
                    "amount": 1 * 100,//response.total_price * 100, // Amount in paise (50000 paise = 500 INR)
                    "currency": "INR",
                    "name": "VANITHA A", // Your business name
                    "description": "Thnak you for buying from us",
                    "image": "https://example.com/your_logo",
                    //"order_id": "order_9A33XWu170gUtm", // Replace with your generated order ID
                    "handler": function (responseb) {
                        alert(responseb.razorpay_payment_id);
                        data = {
                            "fname": fname,
                            "lname": lname,
                            "email": email,
                            "phone": phone,
                            "address": address,
                            "city": city,
                            "state": state,
                            "country": country,
                            "pincode": pincode,
                            "payment_mode": "Paid by Razorpay",
                            "payment_id": responseb.razorpay_payment_id,
                            "csrfmiddlewaretoken": $('input[name=csrfmiddlewaretoken]').val()
                       
                        }
                        $.ajax({
                            method: "POST",
                            url: "/placeorder/",
                            data: data,
                            success: function (responsec) {
                                Swal.fire({
                                    title: "Congratulations!",
                                    text: "Your order has been placed successfully!",
                                    icon: "success"
                                }).then((result) => {
                                    window.location.href = "/my-orders/";
                                });
                            }
                        });
                    },
                    "prefill": { 
                        "name": fname + " " + lname, // Customer's full name
                        "email": email,
                        "contact": phone
                    },
                    "theme": {
                        "color": "#3399cc"
                    }
                };

                var rzp1 = new Razorpay(options);
                rzp1.open();
            }
        });
    });
});
