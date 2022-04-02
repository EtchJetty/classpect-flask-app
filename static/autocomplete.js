$("body").click(function () {
  // Gets clicked on word (or selected text if text is selected)
  var t = "";
  if (window.getSelection && (sel = window.getSelection()).modify) {
    // Webkit, Gecko
    var s = window.getSelection();
    if (s.isCollapsed) {
      s.modify("move", "forward", "character");
      s.modify("move", "backward", "word");
      s.modify("extend", "forward", "word");
      t = s.toString();
      s.modify("move", "forward", "character"); //clear selection
    } else {
      t = s.toString();
    }
  } else if ((sel = document.selection) && sel.type != "Control") {
    // IE 4+
    var textRange = sel.createRange();
    if (!textRange.text) {
      textRange.expand("word");
    }
    // Remove trailing spaces
    while (/\s$/.test(textRange.text)) {
      textRange.moveEnd("character", -1);
    }
    t = textRange.text;
  }
if (t == "") {
          t = "base";
        }
  var cspe = t[0].toUpperCase() + t.slice(1).toLowerCase();
if (document.getElementById("housetrapped")) {
var housetrapped_iframe = document.getElementById("housetrapped");
  if (canonAspects.has(cspe)) {
housetrapped_iframe.setAttribute("src", "https://housetrapped-faq-archive.glitch.me/aspects.html#" + archiveUrls["aspect"][cspe]);  }
  if (canonClasses.has(cspe)) {
housetrapped_iframe.setAttribute("src", "https://housetrapped-faq-archive.glitch.me/classes.html#" + archiveUrls["class"][cspe]);  
  }}
});

const canonAspects = new Set([
  "Blood",
  "Breath",
  "Doom",
  "Heart",
  "Hope",
  "Life",
  "Light",
  "Mind",
  "Rage",
  "Space",
  "Time",
  "Void",
]);
const canonClasses = new Set([
  "Bard",
  "Heir",
  "Knight",
  "Mage",
  "Maid",
  "Page",
  "Prince",
  "Rogue",
  "Seer",
  "Sylph",
  "Thief",
  "Witch",
]);

const archiveUrls = {
  class: {
    Heir: "message-930617558002991145",
    Bard: "message-930634497442082837",
    Witch: "message-930618551340003388",
    Knight: "message-930621209639530586",
    Mage: "message-930620454899691550",
    Maid: "message-930629176384442369",
    Page: "message-930623251254751253",
    Prince: "message-930632811893882930",
    Rogue: "message-930627037918560366",
    Seer: "message-930619500485808128",
    Sylph: "message-930630920136949821",
    Thief: "message-930625653089374300",
  },
  aspect: {
    Blood: "message-930653867153166346",
    Breath: "message-930651171188797460",
    Doom: "message-930649304425701466",
    Heart: "message-930662443884101632",
    Hope: "message-930655170956759060",
    Life: "message-930647614481920040",
    Light: "message-930641626148253707",
    Mind: "message-930660926020001823",
    Rage: "message-930655170956759060",
    Space: "message-930639006083977217",
    Time: "message-930637393206333455",
    Void: "message-930643051888648222",
  },
};
