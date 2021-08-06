import {
    Mark,
    mergeAttributes
} from 'https://cdn.skypack.dev/pin/@tiptap/core@v2.0.0-beta.29-ehyNSRjShPZE49ePTtXD/mode=imports,min/optimized/@tiptap/core.js'

export const SpanExtension = Mark.create({
    name: 'span',

    defaultOptions: {
        HTMLAttributes: {},
    },

    // data-bs-placement="bottom" data-bs-toggle="tooltip" data-bs-html="true" title="{{ item.display_html }}"

    addAttributes() {
        return {
            class_attr: {
                default: null,
                // Customize the HTML parsing (for example, to load the initial content)
                parseHTML: element => {
                    return {
                        class_attr: element.getAttribute('class'),
                    }
                },
                // … and customize the HTML rendering.
                renderHTML: attributes => {
                    return {
                        class: `${attributes.class_attr}`,
                    }
                },
            },
            data_bs_placement: {
                default: null,
                parseHTML: element => {
                    return {
                        data_bs_placement: element.getAttribute('data-bs-placement'),
                    }
                },
                renderHTML: attributes => {
                    let attr = `${attributes.data_bs_placement}`
                    if (attr === 'null') {
                        return {}
                    }
                    return {
                        'data-bs-placement': `${attributes.data_bs_placement}`,
                    }
                },
            },
            data_bs_toggle: {
                default: null,
                parseHTML: element => {
                    return {
                        data_bs_toggle: element.getAttribute('data-bs-toggle'),
                    }
                },
                renderHTML: attributes => {
                    let attr = `${attributes.data_bs_toggle}`
                    if (attr === 'null') {
                        return {}
                    }
                    return {
                        'data-bs-toggle': `${attributes.data_bs_toggle}`,
                    }
                },
            },
            data_bs_html: {
                default: null,
                parseHTML: element => {
                    return {
                        data_bs_html: element.getAttribute('data-bs-html'),
                    }
                },
                renderHTML: attributes => {
                    let attr = `${attributes.data_bs_html}`
                    if (attr === 'null') {
                        return {}
                    }
                    return {
                        'data-bs-html': `${attributes.data_bs_html}`,
                    }
                },
            },
            title: {
                default: null,
                parseHTML: element => {
                    return {
                        title: element.getAttribute('title'),
                    }
                },
                renderHTML: attributes => {
                    let attr = `${attributes.title}`
                    if (attr === 'null') {
                        return {}
                    }
                    return {
                        'title': `${attributes.title}`,
                    }
                },
            },
            data_bs_original_title: {
                default: null,
                parseHTML: element => {
                    return {
                        data_bs_original_title: element.getAttribute('data-bs-original-title'),
                    }
                },
                renderHTML: attributes => {
                    let attr = `${attributes.data_bs_original_title}`
                    if (attr === 'null') {
                        return {}
                    }
                    return {
                        'data-bs-original-title': `${attributes.data_bs_original_title}`,
                    }
                },
            },

        }
    },

    parseHTML() {
        return [
            {
                tag: 'span',
                getAttrs: node => node.hasAttribute('class') && null,
            },
        ]
    },

    renderHTML({HTMLAttributes}) {
        return ['span', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes), 0]
    },

})