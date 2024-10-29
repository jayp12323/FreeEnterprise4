var _pj;
function _pj_snippets(container) {
    function in_es6(left, right) {
        if (((right instanceof Array) || ((typeof right) === "string"))) {
            return (right.indexOf(left) > (- 1));
        } else {
            if (((right instanceof Map) || (right instanceof Set) || (right instanceof WeakMap) || (right instanceof WeakSet))) {
                return right.has(left);
            } else {
                return (left in right);
            }
        }
    }
    container["in_es6"] = in_es6;
    return container;
}
_pj = {};
_pj_snippets(_pj);
class FlagSetCore {
    constructor(flagspec, lib) {
        this._flagspec = flagspec;
        this._lib = lib;
        this._flags = {};
        this._embedded_version = null;
    }
    load(flag_string) {
        if (((flag_string.length > 0) && (flag_string[0] === "b"))) {
            this._load_binary(flag_string);
        } else {
            this._load_text(flag_string);
        }
    }
    _load_text(flag_string) {
        var index, m, subflag_prefix, subflags, superflag;
        this._flags = {};
        this._embedded_version = null;
        index = 0;
        superflag = null;
        flag_string = this._lib.re_sub("\\s", "", flag_string);
        while ((flag_string.length > 0)) {
            m = this._lib.re_search("^[A-Z]", flag_string);
            if (m) {
                superflag = m[0];
                flag_string = flag_string.slice(superflag.length);
                continue;
            }
            m = this._lib.re_search("^-[a-z0-9_]+:?", flag_string);
            if (m) {
                superflag = m[0];
                flag_string = flag_string.slice(superflag.length);
                if ((! this._lib.re_test("\\:$", superflag))) {
                    this.set(superflag);
                }
                continue;
            }
            m = this._lib.re_search("^([a-z0-9_]+:)?([a-z0-9_]+(,[a-z0-9_]+)*)/?", flag_string);
            if (m) {
                if ((superflag === null)) {
                    throw new Error(`Parse error: found subflag without superflag around '${m[0]}'`);
                }
                subflag_prefix = (m[1] ? m[1] : "");
                subflags = m[2].split(",");
                for (var i = 0, _pj_a = subflags.length; (i < _pj_a); i += 1) {
                    this.set(((superflag + subflag_prefix) + subflags[i]));
                }
                flag_string = flag_string.slice(m[0].length);
                continue;
            }
            throw new Error(`Parse error around '${flag_string}'`);
        }
    }
    _load_binary(binary_string) {
        var bit_index, byte_index, byte_list, embedded_version_string, field_size, flag_binary_info, spec_version_string, src_byte, subfield_size, value, value_bit_index;
        binary_string = binary_string.slice(1);
        byte_list = this._lib.b64decode(binary_string);
        if ((byte_list.length < 3)) {
            throw new Error("Binary flag string too short");
        }
        this._embedded_version = byte_list.slice(0, 3);
        for (var i = 0, _pj_a = 3; (i < _pj_a); i += 1) {
            if ((this._embedded_version[i] !== this._flagspec["version"][i])) {
                embedded_version_string = this._lib.join(function () {
    var _pj_b = [], _pj_c = embedded_version_string;
    for (var _pj_d = 0, _pj_e = _pj_c.length; (_pj_d < _pj_e); _pj_d += 1) {
        var v = _pj_c[_pj_d];
        _pj_b.push(v.toString());
    }
    return _pj_b;
}
.call(this), ".");
                spec_version_string = this._lib.join(function () {
    var _pj_b = [], _pj_c = this._flagspec["version"];
    for (var _pj_d = 0, _pj_e = _pj_c.length; (_pj_d < _pj_e); _pj_d += 1) {
        var v = _pj_c[_pj_d];
        _pj_b.push(v.toString());
    }
    return _pj_b;
}
.call(this), ".");
                throw new Error(`Version mismatch: flag string is v${embedded_version_string}, expected v${spec_version_string}`);
            }
        }
        byte_list = byte_list.slice(3);
        this._flags = {};
        for (var i = 0, _pj_a = this._flagspec["binary"].length; (i < _pj_a); i += 1) {
            flag_binary_info = this._flagspec["binary"][i];
            field_size = flag_binary_info["size"];
            byte_index = (flag_binary_info["offset"] >> 3);
            bit_index = (flag_binary_info["offset"] & 7);
            value = 0;
            value_bit_index = 0;
            while ((field_size > 0)) {
                subfield_size = this._lib.min(field_size, (8 - bit_index));
                src_byte = ((byte_index < byte_list.length) ? byte_list[byte_index] : 0);
                value = (value | (((src_byte >> bit_index) & ((1 << subfield_size) - 1)) << value_bit_index));
                value_bit_index += subfield_size;
                field_size -= subfield_size;
                byte_index += 1;
                bit_index = 0;
            }
            if ((value === flag_binary_info["value"])) {
                this.set(flag_binary_info["flag"]);
            }
        }
    }
    get_list(regex = null) {
        var flags;
        flags = [];
        for (var flag, _pj_c = 0, _pj_a = this._flagspec["order"], _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            flag = _pj_a[_pj_c];
            if (this.has(flag)) {
                if (((regex === null) || this._lib.re_test(regex, flag))) {
                    this._lib.push(flags, flag);
                }
            }
        }
        return flags;
    }
    get_suffix(flag_prefix) {
        var flag_regex, flags;
        flag_regex = ("^" + flag_prefix);
        flags = this.get_list(flag_regex);
        if ((flags.length > 0)) {
            return flags[0].slice(flag_prefix.length);
        } else {
            return null;
        }
    }
    get_version() {
        return this._embedded_version;
    }
    has(flag) {
        if ((! _pj.in_es6(flag, this._flagspec["order"]))) {
            throw new Error(`Invalid flag ${flag}`);
        }
        if (_pj.in_es6(flag, this._flagspec["implicit"])) {
            return this._evaluate_condition(this._flagspec["implicit"][flag]);
        } else {
            if (_pj.in_es6(flag, this._flags)) {
                return true;
            } else {
                return false;
            }
        }
    }
    has_any(...flags) {
        for (var flag, _pj_c = 0, _pj_a = flags, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            flag = _pj_a[_pj_c];
            if (this.has(flag)) {
                return true;
            }
        }
        return false;
    }
    has_all(...flags) {
        for (var flag, _pj_c = 0, _pj_a = flags, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            flag = _pj_a[_pj_c];
            if ((! this.has(flag))) {
                return false;
            }
        }
        return true;
    }
    set(flag) {
        if (_pj.in_es6(flag, this._flagspec["implicit"])) {
            return;
        }
        for (var mutex_set, _pj_c = 0, _pj_a = this._flagspec["mutex"], _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            mutex_set = _pj_a[_pj_c];
            if (_pj.in_es6(flag, mutex_set)) {
                for (var other_flag, _pj_f = 0, _pj_d = mutex_set, _pj_e = _pj_d.length; (_pj_f < _pj_e); _pj_f += 1) {
                    other_flag = _pj_d[_pj_f];
                    if ((other_flag !== flag)) {
                        this.unset(other_flag);
                    }
                }
                break;
            }
        }
        this._flags[flag] = true;
    }
    unset(flag) {
        if (_pj.in_es6(flag, this._flags)) {
            delete this._flags[flag];
        }
    }
    parse() {
        var m, results, subflag, subflag_obj, subsubflag, superflag, superflag_obj;
        results = [];
        for (var flag, _pj_c = 0, _pj_a = this._flagspec["order"], _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            flag = _pj_a[_pj_c];
            if ((! this.has(flag))) {
                continue;
            }
            if ((flag[0] === "-")) {
                m = this._lib.re_search("^(-[a-z0-9_]+:?)([a-z0-9_]+)?$", flag);
                superflag = m[1];
                subflag = m[2];
                subsubflag = null;
            } else {
                m = this._lib.re_search("^([A-Z])(([a-z0-9_]+:)?([a-z0-9_]+))?$", flag);
                superflag = m[1];
                subflag = (m[3] ? m[3] : m[4]);
                subsubflag = (m[3] ? m[4] : null);
            }
            superflag_obj = null;
            for (var item, _pj_f = 0, _pj_d = results, _pj_e = _pj_d.length; (_pj_f < _pj_e); _pj_f += 1) {
                item = _pj_d[_pj_f];
                if ((item[0] === superflag)) {
                    superflag_obj = item;
                    break;
                }
            }
            if ((! superflag_obj)) {
                superflag_obj = [superflag, []];
                this._lib.push(results, superflag_obj);
            }
            if (subflag) {
                subflag_obj = null;
                for (var item, _pj_f = 0, _pj_d = superflag_obj[1], _pj_e = _pj_d.length; (_pj_f < _pj_e); _pj_f += 1) {
                    item = _pj_d[_pj_f];
                    if ((item[0] === subflag)) {
                        subflag_obj = item;
                        break;
                    }
                }
                if ((! subflag_obj)) {
                    subflag_obj = [subflag, []];
                    this._lib.push(superflag_obj[1], subflag_obj);
                }
                if (subsubflag) {
                    this._lib.push(subflag_obj[1], subsubflag);
                }
            }
        }
        return results;
    }
    _evaluate_condition(condition) {
        if (this._lib.is_string(condition)) {
            return this.has(condition);
        } else {
            if ((condition[0] === "not")) {
                return (! this._evaluate_condition(condition[1]));
            } else {
                if ((condition[0] === "and")) {
                    for (var subcondition, _pj_c = 0, _pj_a = condition.slice(1), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                        subcondition = _pj_a[_pj_c];
                        if ((! this._evaluate_condition(subcondition))) {
                            return false;
                        }
                    }
                    return true;
                } else {
                    if ((condition[0] === "or")) {
                        for (var subcondition, _pj_c = 0, _pj_a = condition.slice(1), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                            subcondition = _pj_a[_pj_c];
                            if (this._evaluate_condition(subcondition)) {
                                return true;
                            }
                        }
                        return false;
                    } else {
                        throw new Error(`Unsupported condition type ${condition[0]}`);
                    }
                }
            }
        }
    }
    _wrap(text, first_line_width, paragraph_width) {
        var break_index, line_width, lines;
        line_width = first_line_width;
        lines = [];
        while ((text.length > line_width)) {
            break_index = line_width;
            for (var i = (line_width - 1), _pj_a = (- 1); (i < _pj_a); i += (- 1)) {
                if ((((text[i] === ",") || (text[i] === ")")) || (text[i] === " "))) {
                    break_index = (i + 1);
                    break;
                }
            }
            this._lib.push(lines, text.slice(0, break_index));
            text = text.slice(break_index);
            line_width = paragraph_width;
        }
        if ((text.length > 0)) {
            this._lib.push(lines, text);
        }
        return lines;
    }
    to_string(pretty = false, wrap_width = null) {
        var last_superflag, line, lines, paragraph_indent, parsed, parts, prefix, segment, subflag_obj_index, subflag_obj_list, sublines, subsubflags, superflag, superflag_last_index, superflag_prefix;
        parsed = this.parse();
        parts = [];
        lines = [];
        last_superflag = null;
        for (var superflag_obj, _pj_c = 0, _pj_a = parsed, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            superflag_obj = _pj_a[_pj_c];
            if (((! pretty) && (parts.length > 0))) {
                this._lib.push(parts, " ");
            } else {
                if (((pretty && (lines.length > 0)) && (last_superflag[0] !== "-"))) {
                    this._lib.push(lines, "");
                }
            }
            superflag = superflag_obj[0];
            last_superflag = superflag;
            superflag_last_index = (superflag.length - 1);
            superflag_prefix = (superflag + ((pretty && (superflag[superflag_last_index] !== ":")) ? " " : ""));
            this._lib.push(parts, superflag_prefix);
            if ((superflag_obj[1].length > 0)) {
                if ((superflag[0] === "-")) {
                    subsubflags = [];
                    for (var subflag_obj, _pj_f = 0, _pj_d = superflag_obj[1], _pj_e = _pj_d.length; (_pj_f < _pj_e); _pj_f += 1) {
                        subflag_obj = _pj_d[_pj_f];
                        this._lib.push(subsubflags, subflag_obj[0]);
                    }
                    subflag_obj_list = [["", subsubflags]];
                } else {
                    subflag_obj_list = superflag_obj[1];
                }
                subflag_obj_index = 0;
                for (var subflag_obj, _pj_f = 0, _pj_d = subflag_obj_list, _pj_e = _pj_d.length; (_pj_f < _pj_e); _pj_f += 1) {
                    subflag_obj = _pj_d[_pj_f];
                    if ((pretty && (parts.length === 0))) {
                        this._lib.push(parts, " /");
                    }
                    segment = (subflag_obj[0] + this._lib.join(subflag_obj[1], ","));
                    if (pretty) {
                        this._lib.push(parts, segment);
                        paragraph_indent = "   ";
                        line = this._lib.join(parts, "");
                        if ((wrap_width === null)) {
                            sublines = [line];
                        } else {
                            sublines = this._wrap(line, wrap_width, (wrap_width - paragraph_indent.length));
                        }
                        prefix = "";
                        for (var subline, _pj_i = 0, _pj_g = sublines, _pj_h = _pj_g.length; (_pj_i < _pj_h); _pj_i += 1) {
                            subline = _pj_g[_pj_i];
                            this._lib.push(lines, (prefix + subline));
                            prefix = paragraph_indent;
                        }
                        parts = [];
                    } else {
                        if ((subflag_obj_index > 0)) {
                            this._lib.push(parts, "/");
                        }
                        this._lib.push(parts, segment);
                    }
                    subflag_obj_index += 1;
                }
            } else {
                if (pretty) {
                    this._lib.push(lines, parts[0]);
                    parts = [];
                }
            }
        }
        if ((! pretty)) {
            line = this._lib.join(parts, "");
            if ((wrap_width !== null)) {
                line = this._lib.join(this._wrap(line, wrap_width, wrap_width), "\n");
            }
            return line;
        } else {
            return this._lib.join(lines, "\n");
        }
    }
    to_binary() {
        var bit_index, byte_index, byte_list, dst_byte, field_size, subfield_size, subvalue, value;
        byte_list = [];
        for (var i = 0, _pj_a = 3; (i < _pj_a); i += 1) {
            this._lib.push(byte_list, this._flagspec["version"][i]);
        }
        for (var flag_binary_info, _pj_c = 0, _pj_a = this._flagspec["binary"], _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            flag_binary_info = _pj_a[_pj_c];
            if ((! this.has(flag_binary_info["flag"]))) {
                continue;
            }
            value = flag_binary_info["value"];
            field_size = flag_binary_info["size"];
            byte_index = ((flag_binary_info["offset"] >> 3) + 3);
            bit_index = (flag_binary_info["offset"] & 7);
            while ((field_size > 0)) {
                while ((byte_index >= byte_list.length)) {
                    this._lib.push(byte_list, 0);
                }
                dst_byte = byte_list[byte_index];
                subfield_size = this._lib.min(field_size, (8 - bit_index));
                subvalue = (value & ((1 << subfield_size) - 1));
                byte_list[byte_index] = (dst_byte | (subvalue << bit_index));
                value >>= subfield_size;
                field_size -= subfield_size;
                bit_index = 0;
                byte_index += 1;
            }
        }
        return ("b" + this._lib.b64encode(byte_list));
    }
}
class FlagLogicCore {
    constructor(flagspec, lib) {
        this._flagspec = flagspec;
        this._lib = lib;
    }
    _simple_disable(flagset, log, prefix, flags_to_disable) {
        for (var flag, _pj_c = 0, _pj_a = flags_to_disable, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
            flag = _pj_a[_pj_c];
            if (flagset.has(flag)) {
                flagset.unset(flag);
                this._lib.push(log, ["correction", ((prefix + "; removed ") + flag)]);
            }
        }
    }
    _simple_disable_regex(flagset, log, prefix, flags_regex) {
        this._simple_disable(flagset, log, prefix, flagset.get_list(flags_regex));
    }
    fix(flagset) {
        var WACKY_SET_1, WACKY_SET_2, WACKY_SET_3, all_spoiler_flags, ch, challenges, char_objective_flags, distinct_count, distinct_flags, has_unavailable_characters, kmiab_flags, log, mode, only_flags, pass_quest_flags, pool, required_chars, sparse_spoiler_flags, start_exclude_flags, start_include_flags, win_flags;
        log = [];
        if ((flagset.has("Kunsafer") && (! flagset.has("Kmoon")))) {
            flagset.set("Kmoon");
            this._lib.push(log, ["correction", "Kunsafer requires placing key items on the moon; adding Kmoon"]);
        }
        if ((flagset.has("Kforge") && flagset.has("Omode:classicforge"))) {
            this._simple_disable(flagset, log, "Classic forge is incompatible with Kforge", ["Kforge"]);
        }
        if (flagset.has("Kforge")) {
            this._simple_disable_regex(flagset, log, "-smith is incompatible with Kforge", "^-smith:");
        }
        kmiab_flags = flagset.get_list("^Kmiab:");
        if ((flagset.has_any("Ksummon", "Kmoon", "Kforge", "Kpink", "Kmiab:standard", "Kmiab:above", "Kmiab:below", "Kmiab:lst", "Kmiab:all") && (! flagset.has("Kmain")))) {
            flagset.set("Kmain");
            this._lib.push(log, ["correction", "Advanced key item randomizations are enabled; forced to add Kmain"]);
        }
        if ((flagset.has("Owin:crystal") && flagset.has("Omode:ki17"))) {
            flagset.unset("Omode:ki17");
            flagset.set("Omode:ki16");
            this._lib.push(log, ["correction", "Can only collect 16 KIs for an objective with Owin:crystal; changing Omode:ki17 to Omode:ki16"]);
        }
        if (((! flagset.has_any("Ksummon", "Kmoon", "Kforge", "Kpink", "Kmiab:standard", "Kmiab:above", "Kmiab:below", "Kmiab:lst", "Kmiab:all")) && flagset.has("Omode:ki17"))) {
            this._simple_disable(flagset, log, "Cannot replace a key item if all of them are required", ["Pkey", "Kstart:pass"]);
        }
        if (flagset.has("Kvanilla")) {
            this._simple_disable(flagset, log, "Key items not randomized", ["Kunsafe", "Kunsafer", "Kunweighted"]);
            this._simple_disable_regex(flagset, log, "Key items not randomized", "^Kstart:");
        }
        if (flagset.has("Kstart:darkness")) {
            this._simple_disable(flagset, log, "Klatedark is incompatible with starting with Darkness", ["Klatedark"]);
        }
        if (flagset.has("Klatedark")) {
            this._simple_disable(flagset, log, "Klatedark implicitly guarantees safe underground access", ["Kunsafe", "Kunsafer"]);
        }
        if ((flagset.has("Kstart:pass") && (! flagset.has("Pkey")))) {
            flagset.set("Pkey");
            this._lib.push(log, ["correction", "Kstart:pass implies Pkey"]);
        }
        if ((_pj.in_es6("Kmiab:all", kmiab_flags) && (kmiab_flags.length > 1))) {
            this._simple_disable_regex(flagset, log, "All miabs already included", "^Kmiab:(standard|above|below|lst)");
        } else {
            if ((_pj.in_es6("Kmiab:standard", kmiab_flags) && (kmiab_flags.length > 1))) {
                this._simple_disable_regex(flagset, log, "Standard miab inclusion takes priority", "^Kmiab:(above|below|lst)");
            }
        }
        if (flagset.has("Cvanilla")) {
            this._simple_disable_regex(flagset, log, "Characters not randomized", "^C(maybe|distinct:|only:|no:)");
        } else {
            only_flags = flagset.get_list("^Conly:");
            if ((only_flags.length > 0)) {
                this._simple_disable_regex(flagset, log, "Conly:* flag(s) are specified", "^Cno:");
            }
        }
        if (flagset.has("Chero")) {
            this._simple_disable_regex(flagset, log, "Hero challenge includes smith weapon", "^-smith:");
        }
        start_include_flags = flagset.get_list("^Cstart:(?!not_)");
        start_exclude_flags = flagset.get_list("^Cstart:not_");
        if (((start_exclude_flags.length > 0) && (start_include_flags.length > 0))) {
            this._simple_disable_regex(flagset, log, "Inclusive Cstart:* flags are specified", "^Cstart:not_");
        }
        if (((start_include_flags.length > 1) && flagset.has("Cstart:any"))) {
            this._simple_disable_regex(flagset, log, "Cstart:any is specified", "^Cstart:(?!any|not_)");
        }
        if ((flagset.has("Cnekkie") && (flagset.get_list("^Cthrift:").length > 0))) {
            this._simple_disable_regex(flagset, log, "Starting gear specified by Cnekkie", "^Cthrift:");
        }
        if (flagset.has("Tempty")) {
            this._simple_disable_regex(flagset, log, "Treasures are empty", "^Tsparse:");
        }
        if (flagset.has_any("Tempty", "Tvanilla", "Tshuffle")) {
            this._simple_disable_regex(flagset, log, "Treasures are not random", "^Tmaxtier:");
            this._simple_disable_regex(flagset, log, "Treasures are not random", "^Tmintier:");
        }
        if (flagset.has_any("Svanilla", "Scabins", "Sempty")) {
            this._simple_disable_regex(flagset, log, "Shops are not random", "^Sno:([^j]|j.)");
            this._simple_disable(flagset, log, "Shops are not random", ["Sunsafe"]);
        }
        if (flagset.has("Sshuffle")) {
            this._simple_disable(flagset, log, "Shops are only shuffled", ["Sno:life"]);
        }
        if (flagset.has("Bvanilla")) {
            this._simple_disable(flagset, log, "Bosses not randomized", ["Bunsafe"]);
            this._simple_disable_regex(flagset, log, "Bosses not randomized", "^Brestrict:");
        }
        if (flagset.has("Evanilla")) {
            this._simple_disable(flagset, log, "Encounters are vanilla", ["Ekeep:behemoths", "Ekeep:doors", "Edanger"]);
        }
        if (flagset.has_any("-entrancesrando:normal", "-entrancesrando:gated", "-entrancesrando:blueplanet", "-entrancesrando:why", "-entrancesrando:all")) {
            this._simple_disable_regex(flagset, log, "Entrances rando takes priority", "^-doorsrando");
        }
        if ((! flagset.has_any("-entrancesrando:normal", "-entrancesrando:gated", "-entrancesrando:blueplanet", "-entrancesrando:why", "-entrancesrando:all", "-doorsrando:normal", "-doorsrando:gated", "-doorsrando:blueplanet", "-doorsrando:why", "-doorsrando:all"))) {
            this._simple_disable(flagset, log, "Removing doors rando related flags when no doors/entrances option is enabled ", ["-calmness", "-forcesealed"]);
        }
        all_spoiler_flags = flagset.get_list("^-spoil:");
        sparse_spoiler_flags = flagset.get_list("^-spoil:sparse");
        if (((all_spoiler_flags.length > 0) && (all_spoiler_flags.length === sparse_spoiler_flags.length))) {
            this._simple_disable_regex(flagset, log, "No spoilers requested", "^-spoil:sparse");
        }
        if (flagset.has("Onone")) {
            this._simple_disable_regex(flagset, log, "No objectives set", "^O(win|req):");
            this._simple_disable_regex(flagset, log, "No objectives set", "^-exp:objectivebonus");
        } else {
            if ((! flagset.get_list("^Oreq:"))) {
                flagset.set("Oreq:all");
                this._lib.push(log, ["correction", "Required number of objectives not specified; setting Oreq:all"]);
            }
            win_flags = flagset.get_list("^Owin:");
            if ((flagset.has("Omode:classicforge") && (! flagset.has("Owin:crystal")))) {
                flagset.set("Owin:crystal");
                this._lib.push(log, ["correction", "Classic Forge is enabled; forced to add Owin:crystal"]);
            } else {
                if ((win_flags.length === 0)) {
                    flagset.set("Owin:game");
                    this._lib.push(log, ["correction", "Objectives set without outcome specified; added Owin:game"]);
                }
            }
            pass_quest_flags = flagset.get_list("^O\\d+:quest_pass$");
            if (((pass_quest_flags.length > 0) && flagset.has("Pnone"))) {
                flagset.set("Pkey");
                this._lib.push(log, ["correction", "Pass objective is set without a pass flag; forced to add Pkey"]);
            }
            char_objective_flags = flagset.get_list("^O\\d+:char_");
            if ((char_objective_flags.length > 0)) {
                required_chars = [];
                for (var f, _pj_c = 0, _pj_a = char_objective_flags, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                    f = _pj_a[_pj_c];
                    ch = this._lib.re_sub("^O\\d+:char_", "", f);
                    this._lib.push(required_chars, ch);
                }
                if (flagset.has("Cvanilla")) {
                    has_unavailable_characters = false;
                    if (_pj.in_es6("cecil", required_chars)) {
                        has_unavailable_characters = true;
                    } else {
                        if (flagset.has("Cnofree")) {
                            if ((((_pj.in_es6("edward", required_chars) || _pj.in_es6("tellah", required_chars)) || _pj.in_es6("palom", required_chars)) || _pj.in_es6("porom", required_chars))) {
                                has_unavailable_characters = true;
                            }
                        } else {
                            if (flagset.has("Cnoearned")) {
                                if (((((((_pj.in_es6("rydia", required_chars) || _pj.in_es6("kain", required_chars)) || _pj.in_es6("rosa", required_chars)) || _pj.in_es6("yang", required_chars)) || _pj.in_es6("cid", required_chars)) || _pj.in_es6("edge", required_chars)) || _pj.in_es6("fusoya", required_chars))) {
                                    has_unavailable_characters = true;
                                }
                            }
                        }
                    }
                    if (has_unavailable_characters) {
                        this._lib.push(log, ["error", "Character objectives are set for characters that cannot be found in vanilla character assignment"]);
                    }
                } else {
                    only_flags = flagset.get_list("^Conly:");
                    pool = [];
                    if ((only_flags.length > 0)) {
                        for (var f, _pj_c = 0, _pj_a = only_flags, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                            f = _pj_a[_pj_c];
                            ch = this._lib.re_sub("^Conly:", "", f);
                            this._lib.push(pool, ch);
                        }
                    } else {
                        pool = ["cecil", "kain", "rydia", "edward", "tellah", "rosa", "yang", "palom", "porom", "cid", "edge", "fusoya"];
                        for (var f, _pj_c = 0, _pj_a = flagset.get_list("^Cno:"), _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                            f = _pj_a[_pj_c];
                            ch = this._lib.re_sub("^Cno:", "", f);
                            this._lib.remove(pool, ch);
                        }
                    }
                    for (var ch, _pj_c = 0, _pj_a = required_chars, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                        ch = _pj_a[_pj_c];
                        if ((! _pj.in_es6(ch, pool))) {
                            this._lib.push(log, ["error", "Character objectives are set for characters excluded from the randomization."]);
                            break;
                        }
                    }
                    distinct_flags = flagset.get_list("^Cdistinct:");
                    if ((distinct_flags.length > 0)) {
                        distinct_count = Number.parseInt(this._lib.re_sub("^Cdistinct:", "", distinct_flags[0]));
                        if ((distinct_count < required_chars.length)) {
                            this._lib.push(log, ["error", "More character objectives are set than distinct characters allowed in the randomization."]);
                        }
                    }
                }
                if ((flagset.has("Cnofree") && flagset.has("Cnoearned"))) {
                    this._lib.push(log, ["error", "Character objectives are set while no character slots will be filled"]);
                }
            }
            if (((flagset.has("Orandom:char") && flagset.has("Cnoearned")) && flagset.has("Cnofree"))) {
                flagset.unset("Orandom:char");
                this._lib.push(log, ["correction", "Random character objectives in the pool while no character slots will be filled. Removed Orandom:char."]);
            }
            if ((! flagset.get_list("^Orandom:\\d"))) {
                this._simple_disable_regex(flagset, log, "No random objectives specified", "^Orandom:[^\\d]");
            }
        }
        if (flagset.has("Owin:crystal")) {
            this._simple_disable(flagset, log, "Cannot start with crystal on Owin:crystal", ["Kstart:crystal"]);
        }
        challenges = flagset.get_list("^-wacky:");
        if (challenges) {
            WACKY_SET_1 = ["afflicted", "menarepigs", "mirrormirror", "skywarriors", "zombies"];
            WACKY_SET_2 = ["battlescars", "payablegolbez", "tellahmaneuver", "worthfighting"];
            WACKY_SET_3 = [["3point", "afflicted", "battlescars", "menarepigs", "mirrormirror", "skywarriors", "unstackable", "zombies"], ["afflicted", "friendlyfire"], ["battlescars", "afflicted", "zombies", "worthfighting"], ["darts", "musical"], ["3point", "tellahmaneuver"]];
            for (var c, _pj_c = 0, _pj_a = challenges, _pj_b = _pj_a.length; (_pj_c < _pj_b); _pj_c += 1) {
                c = _pj_a[_pj_c];
                mode = this._lib.re_sub("-wacky:", "", c);
                if (_pj.in_es6(mode, WACKY_SET_1)) {
                    this._simple_disable(flagset, log, "Can only have one enforced status wacky mode", function () {
    var _pj_d = [], _pj_e = WACKY_SET_1;
    for (var _pj_f = 0, _pj_g = _pj_e.length; (_pj_f < _pj_g); _pj_f += 1) {
        var m = _pj_e[_pj_f];
        if ((m !== mode)) {
            _pj_d.push(`-wacky:${m}`);
        }
    }
    return _pj_d;
}
.call(this));
                    this._simple_disable(flagset, log, "Modes are incompatible with enforced status wacky modes", function () {
    var _pj_d = [], _pj_e = WACKY_SET_2;
    for (var _pj_f = 0, _pj_g = _pj_e.length; (_pj_f < _pj_g); _pj_f += 1) {
        var m = _pj_e[_pj_f];
        _pj_d.push(`-wacky:${m}`);
    }
    return _pj_d;
}
.call(this));
                }
                for (var group, _pj_f = 0, _pj_d = WACKY_SET_3, _pj_e = _pj_d.length; (_pj_f < _pj_e); _pj_f += 1) {
                    group = _pj_d[_pj_f];
                    if (_pj.in_es6(mode, group)) {
                        this._simple_disable(flagset, log, `Wacky modes are incompatible with ${mode}`, function () {
    var _pj_g = [], _pj_h = group;
    for (var _pj_i = 0, _pj_j = _pj_h.length; (_pj_i < _pj_j); _pj_i += 1) {
        var m = _pj_h[_pj_i];
        if ((m !== mode)) {
            _pj_g.push(`-wacky:${m}`);
        }
    }
    return _pj_g;
}
.call(this));
                    }
                }
            }
        }
        return log;
    }
}

//# sourceMappingURL=flagsetcore.js.map
