/*----------------------------
* jQuery meanMenu v2.0.8
------------------------------*/
!function($){"use strict";$.fn.meanmenu=function(e){var n={meanMenuTarget:jQuery(this),meanMenuContainer:"body",meanMenuClose:"X",meanMenuCloseSize:"18px",meanMenuOpen:"<span /><span /><span />",meanRevealPosition:"right",meanRevealPositionDistance:"0",meanRevealColour:"",meanScreenWidth:"480",meanNavPush:"",meanShowChildren:!0,meanExpandableChildren:!0,meanExpand:"+",meanContract:"-",meanRemoveAttrs:!1,onePage:!1,meanDisplay:"block",removeElements:""};e=$.extend(n,e);var a=window.innerWidth||document.documentElement.clientWidth;return this.each(function(){var n=e.meanMenuTarget,t=e.meanMenuContainer,r=e.meanMenuClose,i=e.meanMenuCloseSize,s=e.meanMenuOpen,u=e.meanRevealPosition,m=e.meanRevealPositionDistance,l=e.meanRevealColour,o=e.meanScreenWidth,c=e.meanNavPush,v=".meanmenu-reveal",h=e.meanShowChildren,d=e.meanExpandableChildren,y=e.meanExpand,j=e.meanContract,Q=e.meanRemoveAttrs,f=e.onePage,g=e.meanDisplay,p=e.removeElements,C=!1;(navigator.userAgent.match(/iPhone/i)||navigator.userAgent.match(/iPod/i)||navigator.userAgent.match(/iPad/i)||navigator.userAgent.match(/Android/i)||navigator.userAgent.match(/Blackberry/i)||navigator.userAgent.match(/Windows Phone/i))&&(C=!0),(navigator.userAgent.match(/MSIE 8/i)||navigator.userAgent.match(/MSIE 7/i))&&jQuery("html").css("overflow-y","scroll");var w="",x=function(){if("center"===u){var e=window.innerWidth||document.documentElement.clientWidth,n=e/2-22+"px";w="left:"+n+";right:auto;",C?jQuery(".meanmenu-reveal").animate({left:n}):jQuery(".meanmenu-reveal").css("left",n)}},A=!1,E=!1;"right"===u&&(w="right:"+m+";left:auto;"),"left"===u&&(w="left:"+m+";right:auto;"),x();var M="",P=function(){M.html(jQuery(M).is(".meanmenu-reveal.meanclose")?r:s)},W=function(){jQuery(".mean-bar,.mean-push").remove(),jQuery(t).removeClass("mean-container"),jQuery(n).css("display",g),A=!1,E=!1,jQuery(p).removeClass("mean-remove")},b=function(){var e="background:"+l+";color:"+l+";"+w;if(o>=a){jQuery(p).addClass("mean-remove"),E=!0,jQuery(t).addClass("mean-container"),jQuery(".mean-container").prepend('<div class="mean-bar"><a href="#nav" class="meanmenu-reveal" style="'+e+'">Show Navigation</a><nav class="mean-nav"></nav></div>');var r=jQuery(n).html();jQuery(".mean-nav").html(r),Q&&jQuery("nav.mean-nav ul, nav.mean-nav ul *").each(function(){jQuery(this).is(".mean-remove")?jQuery(this).attr("class","mean-remove"):jQuery(this).removeAttr("class"),jQuery(this).removeAttr("id")}),jQuery(n).before('<div class="mean-push" />'),jQuery(".mean-push").css("margin-top",c),jQuery(n).hide(),jQuery(".meanmenu-reveal").show(),jQuery(v).html(s),M=jQuery(v),jQuery(".mean-nav ul").hide(),h?d?(jQuery(".mean-nav ul ul").each(function(){jQuery(this).children().length&&jQuery(this,"li:first").parent().append('<a class="mean-expand" href="#" style="font-size: '+i+'">'+y+"</a>")}),jQuery(".mean-expand").on("click",function(e){e.preventDefault(),jQuery(this).hasClass("mean-clicked")?(jQuery(this).text(y),jQuery(this).prev("ul").slideUp(300,function(){})):(jQuery(this).text(j),jQuery(this).prev("ul").slideDown(300,function(){})),jQuery(this).toggleClass("mean-clicked")})):jQuery(".mean-nav ul ul").show():jQuery(".mean-nav ul ul").hide(),jQuery(".mean-nav ul li").last().addClass("mean-last"),M.removeClass("meanclose"),jQuery(M).click(function(e){e.preventDefault(),A===!1?(M.css("text-align","center"),M.css("text-indent","0"),M.css("font-size",i),jQuery(".mean-nav ul:first").slideDown(),A=!0):(jQuery(".mean-nav ul:first").slideUp(),A=!1),M.toggleClass("meanclose"),P(),jQuery(p).addClass("mean-remove")}),f&&jQuery(".mean-nav ul > li > a:first-child").on("click",function(){jQuery(".mean-nav ul:first").slideUp(),A=!1,jQuery(M).toggleClass("meanclose").html(s)})}else W()};C||jQuery(window).resize(function(){a=window.innerWidth||document.documentElement.clientWidth,a>o,W(),o>=a?(b(),x()):W()}),jQuery(window).resize(function(){a=window.innerWidth||document.documentElement.clientWidth,C?(x(),o>=a?E===!1&&b():W()):(W(),o>=a&&(b(),x()))}),b()})}}(jQuery);


/*-------------------------------
   jquery.collapes.js
--------------------------------*/

(function($, exports) {

    // Constructor
    function Collapse (el, options) {
        options = options || {};
        var _this = this,
            query = options.query || "> :even";

        $.extend(_this, {
            $el: el,
            options : options,
            sections: [],
            isAccordion : options.accordion || false,
            db : options.persist ? jQueryCollapseStorage(el.get(0).id) : false
        });

        // Figure out what sections are open if storage is used
        _this.states = _this.db ? _this.db.read() : [];

        // For every pair of elements in given
        // element, create a section
        _this.$el.find(query).each(function() {
            new jQueryCollapseSection($(this), _this);
        });

        // Capute ALL the clicks!
        (function(scope) {
            _this.$el.on("click", "[data-collapse-summary] " + (scope.options.clickQuery || ""),
                $.proxy(_this.handleClick, scope));

            _this.$el.bind("toggle close open",
                $.proxy(_this.handleEvent, scope));

        }(_this));
    }

    Collapse.prototype = {
        handleClick: function(e, state) {
            e.preventDefault();
            state = state || "toggle";
            var sections = this.sections,
                l = sections.length;
            while(l--) {
                if($.contains(sections[l].$summary[0], e.target)) {
                    sections[l][state]();
                    break;
                }
            }
        },
        handleEvent: function(e) {
            if(e.target == this.$el.get(0)) return this[e.type]();
            this.handleClick(e, e.type);
        },
        open: function(eq) {
            this._change("open", eq);
        },
        close: function(eq) {
            this._change("close", eq);
        },
        toggle: function(eq) {
            this._change("toggle", eq);
        },
        _change: function(action, eq) {
            if(isFinite(eq)) return this.sections[eq][action]();
            $.each(this.sections, function(i, section) {
                section[action]();
            });
        }
    };

    // Section constructor
    function Section($el, parent) {

        if(!parent.options.clickQuery) $el.wrapInner('<a href="#"/>');

        $.extend(this, {
            isOpen : false,
            $summary : $el.attr("data-collapse-summary",""),
            $details : $el.next(),
            options: parent.options,
            parent: parent
        });
        parent.sections.push(this);

        // Check current state of section
        var state = parent.states[this._index()];

        if(state === 0) {
            this.close(true);
        }
        else if(this.$summary.is(".open") || state === 1) {
            this.open(true);
        } else {
            this.close(true);
        }
    }

    Section.prototype = {
        toggle : function() {
            this.isOpen ? this.close() : this.open();
        },
        close: function(bypass) {
            this._changeState("close", bypass);
        },
        open: function(bypass) {
            var _this = this;
            if(_this.options.accordion && !bypass) {
                $.each(_this.parent.sections, function(i, section) {
                    section.close();
                });
            }
            _this._changeState("open", bypass);
        },
        _index: function() {
            return $.inArray(this, this.parent.sections);
        },
        _changeState: function(state, bypass) {

            var _this = this;
            _this.isOpen = state == "open";
            if($.isFunction(_this.options[state]) && !bypass) {
                _this.options[state].apply(_this.$details);
            } else {
                _this.$details[_this.isOpen ? "show" : "hide"]();
            }

            _this.$summary.toggleClass("open", state !== "close");
            _this.$details.attr("aria-hidden", state === "close");
            _this.$summary.attr("aria-expanded", state === "open");
            _this.$summary.trigger(state === "open" ? "opened" : "closed", _this);
            if(_this.parent.db) {
                _this.parent.db.write(_this._index(), _this.isOpen);
            }
        }
    };

    // Expose in jQuery API
    $.fn.extend({
        collapse: function(options, scan) {
            var nodes = (scan) ? $("body").find("[data-collapse]") : $(this);
            return nodes.each(function() {
                var settings = (scan) ? {} : options,
                    values = $(this).attr("data-collapse") || "";
                $.each(values.split(" "), function(i,v) {
                    if(v) settings[v] = true;
                });
                new Collapse($(this), settings);
            });
        }
    });

    //jQuery DOM Ready
    $(function() {
        $.fn.collapse(false, true);
    });

    // Expose constructor to
    // global namespace
    exports.jQueryCollapse = Collapse;
    exports.jQueryCollapseSection = Section;

})(window.jQuery, window);

