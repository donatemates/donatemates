$(document).ready(function() {
  var rootUrl = "https://api-sahil.donatemates.com/";

  // Fetch list of charities:

  var $charitySelector = $("#charity");

  $.get(rootUrl + "charities", function(data) {
    $charitySelector.empty();
    for (var i = 0; i < data.length; i++) {
      $charitySelector.append($("<option value='" + data[i]["id"] + "' />").text(data[i].name));
    }
  });

  // Create campaign:

  var $createCampaignTrigger = $(".js-create-campaign-trigger"),
      $form = $("form");

  $(document).on("keyup", "input.error", function() {
    $(this).removeClass("error");
  });

  $(document).on("change keyup paste", "#amount", function() {
    $("#match_cents").val(parseInt($("#amount").val().replace(/,/g, "")) * 100);
  });

  $createCampaignTrigger.click(function(ev) {
    ev.preventDefault();

    var invalidFields = false;
    $form.find("input").map(function() {
      if(!$(this).val()) {
        $(this).addClass('error');
        invalidFields = true;
      }
    });
    if (invalidFields) {
      return false;
    }

    $createCampaignTrigger.text("Creating campaign...");

    $.post(rootUrl + "campaign", $form.serialize()).done(
      function(data) {
        window.location = "campaign.html?id=" + data.campaign_id;
      }
    ).fail(
      function(jqXHR, textStatus, errorThrown) {
        alert(jqXHR.responseText);
        $createCampaignTrigger.text("Create campaign");
      }
    );
  });

  // Refresh campaign data:

  var QueryString = function() {
    // This function is anonymous, is executed immediately and 
    // the return value is assigned to QueryString!
    var query_string = {};
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i = 0; i < vars.length; i++) {
      var pair = vars[i].split("=");
      // If first entry with this name
      if (typeof query_string[pair[0]] === "undefined") {
        query_string[pair[0]] = decodeURIComponent(pair[1]);
      // If second entry with this name
      } else if (typeof query_string[pair[0]] === "string") {
        var arr = [query_string[pair[0]],decodeURIComponent(pair[1])];
        query_string[pair[0]] = arr;
      // If third or later entry with this name
      } else {
        query_string[pair[0]].push(decodeURIComponent(pair[1]));
      }
    } 
    return query_string;
  }();

  var formatCurrency = function(amount_cents) {
    if (amount_cents == 0) {
      return "$0";
    }
    var value = amount_cents / 100;
    var num = '$' + value.toFixed(2).replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,");
    return num.replace(/\.00$/,'');
  };

  window.fetchData = function() {
    $.get(rootUrl + "campaign/" + QueryString.id, function(data) {
      var matchedPercentage = data.donation_total_cents / data.match_cents + "%";

      $("#template-container").loadTemplate("#template", {
        campaignerName: data.campaigner_name,
        matchAmount: formatCurrency(data.match_cents),
        charityName: data.charity_name,
        matchedAmount: formatCurrency(data.donation_total_cents),
        matchedPercentage: matchedPercentage,
        recentDonors: data.recent_donors,
        topDonors: data.large_donors,
        donationEmail: data.donation_email
      });

      $("#progress").style('width', matchedPercentage);

      $("#recent-donors").empty();
      for (var i = 0; i < data.recent_donors; i++) {
        var donation = data.recent_donors[i];
        $("#recent-donors").append($("<li />").text(formatCurrency(donation.donation_cents) + " by " + donation.donor_name));
      }

      $("#large-donors").empty();
      for (var i = 0; i < data.large_donors; i++) {
        var donation = data.large_donors[i];
        $("#large-donors").append($("<li />").text(formatCurrency(donation.donation_cents) + " by " + donation.donor_name));
      }

      $("#donation-link").attr("href", data.donation_url);
    }).fail(function() {
      $(".fourohfour-indicator").show();
    });
  };
});
